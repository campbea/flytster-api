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

#### Users
- [Register a new user](#register-a-new-user)
- [Login a user](#login-a-user)
- [Logout a user](#logout-a-user)
- [Get the users profile](#get-the-users-profile)
- [Update the users profile](#update-the-users-profile)
- [Verify a users email](#verify-a-users-email)
- [Change the users password](#change-the-users-password)
- [Request a password reset](#request-a-password-reset)
- [Reset a users password](#reset-a-users-password)

#### Passengers
- [Create a passenger](#create-a-passenger)
- [List all passengers](#list-all-passengers)
- [Get a passenger](#get-a-passenger)
- [Update a passenger](#update-a-passenger)

#### Trips
- [Create a trip](#create-a-trip)
- [List all trips](#list-all-trips)
- [Get a trip](#get-a-trip)


## API Routes


### Users
Flytster users only require an email to create an account. After creating an account, a user will have to verify their email address by clicking a link. Process for a verified user: Find a flight -> Add all of the passengers information -> Confirm booking -> Complete payment.

#### Register a new user

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
- Registering a user will return a valid API auth token.

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


#### Login a user

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


#### Logout a user

**DELETE:** `/api/v1/user/logout`

**Notes:**
- Deletes the current auth token for the user.

**Response:** None

**Status Codes:**
- `204` if successful


#### Get the users profile

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


#### Update the users profile

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
- A user cannot update their profile until `is_verified` is true
- If the user updates their email the user will receive an email containing a link to verify the new email (verification token is in link). Until the user verifies their token, the updated email will remain in email_pending.

**Response:**
```json
{
    "id": 5,
    "first_name": "Tom",
    "last_name": "Brady",
    "email": "test@test.com",
    "email_pending": "braddytime@gmail.com",
    "is_verified": true,
    "timestamp": "2016-02-14T23:19:26.513620Z"
}
```

**Status Codes:**
- `200` if successful
- `400` if incorrect data is provided
- `403` if user is not authorized or verified


#### Verify a users email

**POST:** `/v1/user/verify_email/`

**Body:**
```json
{
    "code": "12dfg2wer6a342g23456",
}
```

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


#### Change the users password

**POST:** `/v1/user/change-password/`

**Body:**
```json
{
    "old_password": "oldpass1",
    "new_password": "newpass1"
}
```

**Notes:**
- `old_password`: must be at least 8 chars with at least 1 number
- `new_password`: must be at least 8 chars with at least 1 number

**Response:** None

**Status Codes:**
- `200` if successful
- `400` if invalid data is provided, or `old_password` doesn't match


#### Request a password reset

**POST:** `/v1/user/request-password/`

**Body:**
```json
{
    "email": "test@test.com",
}
```

**Notes:**
- `email` can be any valid email address. The reset code will be emailed to the user.

**Response:** None

**Status Codes:**
- `200` if successful
- `400` is bad data is sent
- `404` if the email is not found


#### Reset a users password

**POST:** `/v1/user/reset-password/`

**Body:**
```json
{
    "token": "12dfg2wer6a342g23456",
    "new_password": "newpass1"
}
```

**Notes:**
- `password`: must be at least 8 chars with at least 1 number
- `token`: verification token is a 20 character combinations of lowercase letters and digits

**Response:** None

**Status Codes:**
- `200` if successful
- `400` is bad data is sent
- `404` if the token is invalid or expired


### Passengers
Passengers are all of the individuals who will be flying on the purchased trip. Their full name must be exactly how it is on their government id. Their phone is required just in case we need to contact them. For each trip, a passengers phone and birthdate must be unique together to ensure that the same passenger was not added multiple times.


#### Create a passenger

**POST:** `/api/v1/passenger/`

**Body:**
```json
{
    "trip_id": 1,
    "first_name": "Tom",
    "middle_name": "Edward Patrick",
    "last_name": "Brady",
    "phone": "1234567890",
    "gender": "M",
    "birthdate": "1111-11-11"
}
```

**Notes:**
- `middle_name`: Not required
- `phone`: A ten-digit US phone number as string
- `gender`: Choices are `M` or `F`
- `birthdate`: ISO format date string `YYYY-MM-DD`
- `trip_id`, `phone` and `birthdate` must be unique together. This is to prevent a user inputing the same passenger twice. However, a user can input a contact phone number multiple times for different passengers.

**Response:**
```json
{
    "id": 7,
    "user": 1,
    "trip": 1,
    "first_name": "Tom",
    "middle_name": "Edward Patrick",
    "last_name": "Brady",
    "phone": "1234567890",
    "gender": "M",
    "birthdate": "1111-11-11",
    "timestamp": "2016-02-26T16:56:03.989179Z"
}
```

**Status Codes:**
- `201` if successfully created
- `400` if incorrect data is provided
- `409` if passenger with `phone` and `birthdate` exists for this trip


#### List all passengers

**GET:** `/api/v1/passenger/`

**NOTES:**
- This will return a list of all unique passengers based on their `phone` and `birthdate`

**Response:**
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "user": 1,
      "trip": 1,
      "first_name": "Peyton",
      "middle_name": "",
      "last_name": "Manning",
      "phone": "1234567890",
      "gender": "M",
      "birthdate": "1111-11-11",
      "timestamp": "2016-02-26T16:56:03.989179Z"
    },
    {
      "id": 2,
      "user": 1,
      "trip": 1,
      "first_name": "Eli",
      "middle_name": "",
      "last_name": "Manning",
      "phone": "1234567890",
      "gender": "M",
      "birthdate": "2222-22-22",
      "timestamp": "2016-02-26T02:03:46.130975Z"
    }
  ]
}
```

**Status Codes:**
- `200` if successful
- `403` if user is not authenticated


#### Get a passenger

**GET:** `/api/v1/passenger/:id`

**Response:**
```json
{
    "id": 7,
    "user": 1,
    "trip": 1,
    "first_name": "Tom",
    "middle_name": "Edward Patrick",
    "last_name": "Brady",
    "phone": "1234567890",
    "gender": "M",
    "birthdate": "1111-11-11",
    "timestamp": "2016-02-26T16:56:03.989179Z"
}
```

**Status Codes:**
- `200` if successful
- `403` if user is not authenticated or owner
- `404` if passenger is not found


#### Update a passenger

**PATCH:** `/api/v1/passenger/:id`

**Body:**
```json
{
    "middle_name": "Edward Patrick",
    "phone": "1234567890",
    "gender": "M",
    "birthdate": "1111-11-11"
}
```

**Response:**
```json
{
    "id": 7,
    "user": 1,
    "trip": 1,
    "first_name": "Tom",
    "middle_name": "Edward Patrick",
    "last_name": "Brady",
    "phone": "1234567890",
    "gender": "M",
    "birthdate": "1111-11-11",
    "timestamp": "2016-02-26T16:56:03.989179Z"
}
```

**Status Codes:**
- `200` if successful
- `400` if `trip`, `phone` and `birthdate` are not unique together
- `403` if user is not authorized or owner
- `404` if passenger is not found


### Trips

A trip is makes up all of the user's flights purchased at once. A trip can be one-way, round-trip, or multi-city. Each trip instance has a status dict field. This field represents the current status of the trip as it goes through the booking & ticketing process. Trips are booked with Sabre and will be ticketed through a local host agency.

**STATUSES:**
- `is_selected`: Defaults to true when a trip is initially created,
- `is_confirmed`: Becomes true after passenger information is completed,
- `is_sabre_successful`: Becomes true after Sabre booking is successful,
- `is_purchased`: Becomes true after passenger successfully purchase ticket,
- `is_ticketed`: Becomes true once ticketing is successful
- `is_expired`: Becomes true once the current date equals the departure date,


#### Create a trip

**POST:** `/api/v1/trip/`

**Notes:**
- This route will be used every time a user selects a trip (The next step for the user would be inputing passenger information).
- `trip_option` is the Google QPX tripOption a user selected. The following trip example below is a round trip from Chicago ORD to Denver DEN departing on `2016-02-16` and returning on `2016-02-17`. IMPORTANT: `trip_option` must be a Google QPX tripOption and have `kind`, `id`, `slice` and `purchase` field. The value of `kind` must be `qpxexpress#tripOption`.

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
      "is_ticketed": false,
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


#### List all trips

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
        "is_ticketed": false,
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
        "is_ticketed": false,
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


#### Get a trip

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
      "is_ticketed": false,
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


#### Create a trip purchase (not started)

**POST:** `/api/v1/trip/purchase`

**Notes:**
- This route will start the flight booking process: approve user's payment, create a trip, book flight through Sabre and then charge the user. The response will display the current status of the process. The process will complete once a trip_id is returned.


#### Get status of a trip (not started)

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
