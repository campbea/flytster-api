# Flytster API Documentation


## Flytster

Flytster is a web application where users purchase flights for the cheapest price. So how does Flyster work? First one finds and purchases a flight with a departure date less than 6 months away. Then if the price of the flight decreases before one's departure, the purchaser receives credit equal to the difference. The user can then apply that credit to their next flight purchase through Flytster.   

To obtain airline information Flytster uses Google's [QPX Express API](https://developers.google.com/qpx-express/).


## Environment Variables

There are a few configurations managed as environment variables. In the development environment, these are injected by Docker Compose and managed in the `docker-compose.yml` file.

* `DATABASE_URL` - This is the connection URL for the PostgreSQL database. It is not used in the **development environment**.
* `DEBUG` - This toggles debug mode for the app to True/False.
* `SECRET_KEY` - This is a secret string. It is used to encrypt and verify the authentication token on routes that require authentication. This is required. The app won't start without it.
* `SERVER_KEY` - Google's API key to keep track of app credentials


## API Table of Contents

#### Users & profiles
- [Register a new user](#register-a-new-user)
- [Login a user](#login-a-user)
- [Logout a user](#logout-a-user)
- [Get the users profile](#get-the-users-profile)
- [Update the users profile](#get-the-users-profile)
- [Verify a users email](#verify-a-users-email)
- [Change the users password](#change-the-users-password)
- [Request a password reset](#request-a-password-reset)
- [Reset a users password](#reset-a-users-password)

#### Trip Searches
- [Create a trip search](#create-a-trip-search)
- [List all trip searches](#list-all-trip-searches)
- [Get a trip search](#get-a-trip-search)
- [Delete a trip search](#delete-a-trip-search)

#### Trip & Status
- [Get status of a trip](#get-status-of-a-trip)


## API Routes


### Register a new user

**POST:** `/api/v1/user/register`

**Body:**
```json
{
    "first_name": "Cam",
    "last_name": "Newton",
    "email": "test@test.com",
    "password": "password1"
}
```

**Notes:**
- `email`: user's email address, must be unique (string)
- `password`: must be at least 8 chars with at least 1 number (string)
- The new user will receive an email containing a link to verify (verification token is in link)

Registering a user will return a valid API auth token.

**Response:**
```json
{
    "id": 5,
    "first_name": "Cam",
    "last_name": "Newton",
    "email": "test@test.com",
    "token": "6ba2103f4ac8a9712ffb2a689b0e",
    "is_verified": false,
    "timestamp": "2016-02-14T23:19:26.513620Z"
}
```

**Status Codes:**
- `201` if successfully created
- `400` if incorrect data is provided
- `409` if the email already exist


### Login a user

**POST:** `/api/v1/user/login`

**Body:**
```json
{
    "email": "test@test.com",
    "password": "password1"
}
```

**Response:**
```json
{
    "id": 5,
    "first_name": "Cam",
    "last_name": "Newton",
    "email": "test@test.com",
    "token": "6ba2103f4ac8a9712ffb2a689b0e",
    "is_verified": false,
    "timestamp": "2016-02-14T23:19:26.513620Z"
}
```

**Status Codes:**
- `201` if successful
- `400` if invalid data is sent
- `403` if email and/or password are incorrect


### Logout a user

**DELETE:** `/api/v1/user/logout`

**Notes:**
Deletes the current auth token for the user; `login` to obtain a new one.

**Response:** None

**Status Codes:**
- `204` if successful


### Get the users profile

**GET:** `/api/v1/user/`

**Response:**
```json
{
    "id": 5,
    "first_name": "Cam",
    "last_name": "Newton",
    "email": "test@test.com",
    "email_pending": null,
    "is_verified": false,
    "timestamp": "2016-02-14T23:19:26.513620Z"
}
```

**Status Codes:**
- `200` if successful
- `403` if no/incorrect token


### Update the users profile

**PATCH:** `/api/v1/user`

**Body:**
```json
{
    "first_name": "Tom",
    "last_name": "Brady",
    "email": "bradytime@gmail.com"
}
```

**Notes:**
- If the user updates their email the user will receive an email containing a link to verify the new email (verification token is in link). Until the user verifies their token, the updated email will remain in email_pending.

**Response:**
```json
{
    "id": 5,
    "first_name": "Tom",
    "last_name": "Brady",
    "email": "test@test.com",
    "email_pending": "braddytime@gmail.com"
    "is_verified": false,
    "timestamp": "2016-02-14T23:19:26.513620Z"
}
```

**Status Codes:**
- `200` if successful
- `400` if incorrect data is provided
- `403` if user is not authorized


### Verify a users email

**POST:** `/v1/user/verify_email/`

**Body:**
```json
{
    "code": "12dfg2wer6a342g23456",
}
```

**Response:** None

**Notes:**
- `code`: Email verification codes are 20 character combinations of lowercase letters and digits

**Response:**
```json
{
    "id": 5,
    "first_name": "Tom",
    "last_name": "Brady",
    "email": "test@test.com",
    "email_pending": null,
    "is_verified": true,
    "timestamp": "2016-02-14T23:19:26.513620Z"
}
```

**Status Codes:**
- `200` if successful
- `400` is bad data is sent
- `404` if the code is invalid or expired


### Change the users password

**POST:** `/v1/user/change-password/`

**Body:**
```json
{
    "old_password": "oldpass1",
    "new_password": "newpass1"
}
```

**Response:** None

**Notes:**
- `old_password`: must be at least 8 chars with at least 1 number
- `new_password`: must be at least 8 chars with at least 1 number


**Status Codes:**
- `200` if successful
- `400` if invalid data is provided, or `old_password` doesn't match


### Request a password reset

**POST:** `/v1/user/request-password/`

**Body:**
```json
{
    "email": "test@test.com",
}
```

**Response:** None

**Notes:**
- `email` can be any valid email address. The reset code will be emailed to the user.

**Status Codes:**
- `200` if successful
- `400` is bad data is sent
- `404` if the email is not found


### Reset a users password

**POST:** `/v1/user/reset-password/`

**Body:**
```json
{
    "token": "12dfg2wer6a342g23456",
    "new_password": "newpass1"
}
```

**Response:** None

**Notes:**
- `password`: must be at least 8 chars with at least 1 number
- `token`: verification token is a 20 character combinations of lowercase letters and digits


**Status Codes:**
- `200` if successful
- `400` is bad data is sent
- `404` if the token is invalid or expired


### Create a trip

**POST:** `/api/v1/trip/`

**Notes:**
- This route will be used every time a user selects a trip after a search and is on the trip's detail page. The next step would be for the user to select checkout, or some other button to move on to purchasing. This info will be saved in order to speed up the checkout process and allow the user to reference their past searches.
- `trip_option` is the tripOption a user selected. The trip body example is a round trip from Chicago ORD to Denver DEN departing on `2016-02-16` and returning on `2016-02-17`. IMPORTANT: `trip_option` must be a Google QPX tripOption and have `kind`, `id`, `slice` and `purchase` field. The value of `kind` must be `qpxexpress#tripOption`.

**Body:**
```json
{
  "trip_option": {
    "kind": "qpxexpress#tripOption",
    "saleTotal": "USD286.20",
    "id": "dfeVRNNDeQKQ1wRSjTu31G001",
    "slice": [
      {
        "kind": "qpxexpress#sliceInfo",
        "duration": 159,
        "segment": [
          {
            "kind": "qpxexpress#segmentInfo",
            "duration": 159,
            "flight": {
              "carrier": "NK",
              "number": "847"
            },
            "id": "GRVECUxTw70vJ0tX",
            "cabin": "COACH",
            "bookingCode": "Y",
            "bookingCodeCount": 4,
            "marriedSegmentGroup": "0",
            "leg": [
              {
                "kind": "qpxexpress#legInfo",
                "id": "LJXwJbKqnxTa3M7W",
                "aircraft": "320",
                "arrivalTime": "2016-02-16T14:04-07:00",
                "departureTime": "2016-02-16T12:25-06:00",
                "origin": "ORD",
                "destination": "DEN",
                "originTerminal": "3",
                "duration": 159,
                "onTimePerformance": 80,
                "mileage": 885,
                "secure": true
              }
            ]
          }
        ]
      },
      {
        "kind": "qpxexpress#sliceInfo",
        "duration": 151,
        "segment": [
          {
            "kind": "qpxexpress#segmentInfo",
            "duration": 151,
            "flight": {
              "carrier": "NK",
              "number": "630"
            },
            "id": "G+kXUtDqIMFX4Z5l",
            "cabin": "COACH",
            "bookingCode": "R",
            "bookingCodeCount": 4,
            "marriedSegmentGroup": "1",
            "leg": [
              {
                "kind": "qpxexpress#legInfo",
                "id": "Lv8L4zSGi8WBXhSj",
                "aircraft": "320",
                "arrivalTime": "2016-02-17T17:06-06:00",
                "departureTime": "2016-02-17T13:35-07:00",
                "origin": "DEN",
                "destination": "ORD",
                "destinationTerminal": "3",
                "duration": 151,
                "onTimePerformance": 70,
                "mileage": 885,
                "secure": true
              }
            ]
          }
        ]
      }
    ],
    "pricing": [
      {
        "saleTotal": "USD286.20",
        "fareCalculation": "CHI NK DEN Q18.60 Q4.65 147.91YNR NK CHI Q18.60 Q4.65 45.58RNR USD 239.99 END ZP ORD DEN XT 18.01US 8.00ZP 11.20AY 9.00XF ORD4.50 DEN4.50",
        "baseFareTotal": "USD239.99",
        "kind": "qpxexpress#pricingInfo",
        "saleTaxTotal": "USD46.21",
        "latestTicketingTime": "2016-02-16T10:25-05:00",
        "saleFareTotal": "USD239.99",
        "ptc": "ADT",
        "fare": [
          {
            "carrier": "NK",
            "kind": "qpxexpress#fareInfo",
            "origin": "CHI",
            "basisCode": "YNR",
            "destination": "DEN",
            "id": "A+2CScErZefeLB8STqkhnLUDbuPHvoW8d2mSGczs"
          },
          {
            "carrier": "NK",
            "kind": "qpxexpress#fareInfo",
            "origin": "DEN",
            "basisCode": "RNR",
            "destination": "CHI",
            "id": "Aplj9coCfvfdtoY9NJA4IgAAPsOi/5tOnLwy7xDA"
          }
        ],
        "passengers": {
          "kind": "qpxexpress#passengerCounts",
          "adultCount": 1
        },
        "tax": [
          {
            "code": "US",
            "chargeType": "GOVERNMENT",
            "kind": "qpxexpress#taxInfo",
            "country": "US",
            "id": "US_001",
            "salePrice": "USD18.01"
          },
          {
            "code": "AY",
            "chargeType": "GOVERNMENT",
            "kind": "qpxexpress#taxInfo",
            "country": "US",
            "id": "AY_001",
            "salePrice": "USD11.20"
          },
          {
            "code": "XF",
            "chargeType": "GOVERNMENT",
            "kind": "qpxexpress#taxInfo",
            "country": "US",
            "id": "XF",
            "salePrice": "USD9.00"
          },
          {
            "code": "ZP",
            "chargeType": "GOVERNMENT",
            "kind": "qpxexpress#taxInfo",
            "country": "US",
            "id": "ZP",
            "salePrice": "USD8.00"
          }
        ],
        "segmentPricing": [
          {
            "segmentId": "GRVECUxTw70vJ0tX",
            "kind": "qpxexpress#segmentPricing",
            "fareId": "A+2CScErZefeLB8STqkhnLUDbuPHvoW8d2mSGczs"
          },
          {
            "segmentId": "G+kXUtDqIMFX4Z5l",
            "kind": "qpxexpress#segmentPricing",
            "fareId": "Aplj9coCfvfdtoY9NJA4IgAAPsOi/5tOnLwy7xDA"
          }
        ]
      }
    ]
  }  
}
```

**Response:**
```json
{
    "id": 1,
    "user": 1,
    "cheapest_price": 50.5,
    "status": {
      "is_selected": true,
      "is_confirmed": false,
      "is_sabre_successful": false,
      "is_purchased": false,
      "is_expired": false,
      "updated": "2016-02-21T04:59:22.173893Z"
    },
    "data": {"..."},
    "timestamp": "2016-02-21T04:59:22.179752Z"
}
```

**Status Codes:**
- `201` if successful
- `400` if data is in incorrect format
- `403` if user is not authenticated


### List all trips

**GET:** `/api/v1/trip/`

**Notes:**
- Returns all non-expired trips for the user. The trips are returned by most recent `timestamp`.

**RESPONSE:**
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "user": 1,
      "cheapest_price": 50.5,
      "status": {
        "is_selected": true,
        "is_confirmed": false,
        "is_sabre_successful": false,
        "is_purchased": false,
        "is_expired": false,
        "updated": "2016-02-21T04:59:22.173893Z"
      },
      "data": {"..."},
      "timestamp": "2016-02-21T04:59:22.179752Z"
    },
    {
      "id": 1,
      "user": 1,
      "cheapest_price": 50.5,
      "status": {
        "is_selected": true,
        "is_confirmed": false,
        "is_sabre_successful": false,
        "is_purchased": false,
        "is_expired": false,
        "updated": "2016-02-21T04:59:22.173893Z"
      },
      "data": {"..."},
      "timestamp": "2016-02-21T04:59:22.179752Z"
    }
  ]
}
```

**Status Codes:**
- `200` if successful
- `403` if user is not authenticated


### Retrieve a trip

**GET:** `/api/v1/trip/:id`

**RESPONSE:**
```json
{
    "id": 1,
    "user": 1,
    "cheapest_price": 50.5,
    "status": {
      "is_selected": true,
      "is_confirmed": false,
      "is_sabre_successful": false,
      "is_purchased": false,
      "is_expired": false,
      "updated": "2016-02-21T04:59:22.173893Z"
    },
    "data": {"..."},
    "timestamp": "2016-02-21T04:59:22.179752Z"
}
```

**Status Codes:**
- `200` if successful
- `403` if user is not authenticated
- `404` if trip search does not exist


### Create a trip purchase (not started)

**POST:** `/api/v1/trip/purchase`

**Notes:**
- This route will start the flight booking process: approve user's payment, create a trip, book flight through Sabre and then charge the user. The response will display the current status of the process. The process will complete once a trip_id is returned.


### Get status of a trip (not started)

**GET:** `/api/v1/trip/status`

**Response:**
```json
{
    "id": 1,
    "cc_approved": true,
    "trip_created": true,
    "sabre_successful": true,
    "cc_charged": true,
    "trip_id": 1,
    "updated": "2016-02-14T23:19:26.513620Z"
}
```

**Status Codes:**
- `200` if successful
- `403` if no/incorrect token
