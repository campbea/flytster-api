# Flytster API Documentation


## Flytster

Flytster is a web/iOS application where users purchase flights for the cheapest price. So how does Flyster work? First one finds and purchases a flight with a departure date less than 6 months away. Then if the price of the flight decreases before one's departure, the purchaser receives credit equal to the difference. The user can then apply that credit to their next flight purchase through Flytster.   

To obtain airline information Flytster uses Google's [QPX Express API](https://developers.google.com/qpx-express/).


## Environment Variables

There are a few configurations managed as environment variables. In the development environment, these are injected by Docker Compose and managed in the `docker-compose.yml` file.

* `DATABASE_URL` - This is the connection URL for the PostgreSQL database. It is not used in the **development environment**.
* `DEBUG` - This toggles debug mode for the app to True/False.
* `SECRET_KEY` - This is a secret string. It is used to encrypt and verify the authentication token on routes that require authentication. This is required. The app won't start without it.
* `SERVER_KEY` - Google's API key to keep track of app credentials
* `TWILIO_ACCOUNT_ID` - Twilio account id
* `TWILIO_API_TOKEN` - Twilio authentication token
* `TWILIO_NUMBER` - Flyter's twilio phone number in +1xxxxxxxxxx format


## API Table of Contents

#### Users
- [Register a new user](#register-a-new-user)
- [Login a user](#login-a-user)
- [Logout a user](#logout-a-user)
- [Get the users profile](#get-the-users-profile)
- [Update the users profile](#update-the-users-profile)
- [Verify a users email](#verify-a-users-email)
- [Verify a users phone](#verify-a-users-phone)
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
- [Check trip availability](#check-trip-availability)


## API Routes


### Users
Flytster users only require an email to create an account. After creating an account, a user will have to verify their email address by clicking a link. Further in the booking process the user will need to provide his/her phone number and then validate the number as well. Process for a verified user: Find a flight -> Add all of the passengers information -> Confirm booking -> Complete payment.

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
    "id": 1,
    "first_name": "Cam",
    "last_name": "Newton",
    "email": "test@test.com",
    "phone": null,
    "email_verified": false,
    "phone_verified": false,
    "recieve_notifications": true,
    "token": "9ddef56c29bf466199289615fd43ad4e",
    "timestamp": "2016-02-29T17:55:19.363236Z"
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
    "id": 1,
    "first_name": "Cam",
    "last_name": "Newton",
    "email": "test@test.com",
    "phone": null,
    "email_verified": false,
    "phone_verified": false,
    "recieve_notifications": true,
    "token": "9ddef56c29bf466199289615fd43ad4e",
    "timestamp": "2016-02-29T17:55:19.363236Z"
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
    "id": 1,
    "first_name": "Cam",
    "last_name": "Newton",
    "email": "test@test.com",
    "phone": null,
    "email_verified": false,
    "phone_verified": false,
    "recieve_notifications": true,
    "token": "9ddef56c29bf466199289615fd43ad4e",
    "timestamp": "2016-02-29T17:55:19.363236Z"
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
    "email": "bradytime@gmail.com",
    "phone": "3174554303"
}
```

**Notes:**
- `phone`: A ten-digit US phone number as string
- When a user updates `email`, the user will receive a verification email. `email_verified` will remain false and `email` will remain their old email until the user verifies their email token.
- When a user updates `phone`, the user will receive a verification text. `phone_verified` will remain false and `phone` will remain null until the user verifies their phone token.

**Response:**
```json
{
    "id": 1,
    "first_name": "Tom",
    "last_name": "Brady",
    "email": "flytster@gmail.com",
    "phone": null,
    "email_pending": "bradytime@gmail.com",
    "email_verified": false,
    "phone_pending": "3174554303",
    "phone_verified": false,
    "recieve_notifications": true,
    "timestamp": "2016-02-29T17:55:19.363236Z"
}
```

**Status Codes:**
- `200` if successful
- `400` if incorrect data is provided
- `403` if user is not authorized or verified


#### Verify a users email

**POST:** `/v1/user/verify-email/`

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
    "id": 1,
    "first_name": "Tom",
    "last_name": "Brady",
    "email": "bradytime@gmail.com",
    "phone": null,
    "email_pending": null,
    "email_verified": true,
    "phone_pending": "3174554303",
    "phone_verified": false,
    "recieve_notifications": true,
    "timestamp": "2016-02-29T17:55:19.363236Z"
}
```

**Status Codes:**
- `200` if successful
- `400` is bad data is sent
- `403` if user is not authenticated
- `404` if the code is invalid or expired


#### Verify a users phone

**POST:** `/v1/user/verify-phone/`

**Body:**
```json
{
    "code": "abc123",
}
```

**Notes:**
- `code`: Phone verification codes are 6 character combinations of lowercase letters and digits

**Response:**
```json
{
    "id": 1,
    "first_name": "Tom",
    "last_name": "Brady",
    "email": "bradytime@gmail.com",
    "phone": "3174554303",
    "email_pending": null,
    "email_verified": true,
    "phone_pending": null,
    "phone_verified": true,
    "recieve_notifications": true,
    "timestamp": "2016-02-29T17:55:19.363236Z"
}
```

**Status Codes:**
- `200` if successful
- `400` is bad data is sent
- `403` if user is not authenticated
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
- `403` if user is not authenticated


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
Passengers are all of the individuals who will be flying on the purchased trip. Their full name must be exactly how it is on their government id. For each trip, a passengers full name and birthdate must be unique together to ensure that the same passenger was not added multiple times.


#### Create a passenger

**POST:** `/api/v1/passenger/`

**Body:**
```json
{
    "trip_id": 1,
    "first_name": "Rob",
    "last_name": "Gronk",
    "gender": "M",
    "birthdate": "1111-11-11"
}
```

**Notes:**
- `middle_name`: Not required
- `gender`: Choices are `M` or `F`
- `birthdate`: ISO format date string `YYYY-MM-DD`
- `trip_id`, `first_name`, `last_name` and `birthdate` must be unique together. This is to prevent a user inputing the same passenger twice.

**Response:**
```json
{
    "id": 1,
    "user": 1,
    "trip": 1,
    "first_name": "Rob",
    "middle_name": "",
    "last_name": "Gronk",
    "gender": "M",
    "birthdate": "1111-11-11",
    "timestamp": "2016-02-29T18:25:31.177351Z"
}
```

**Status Codes:**
- `201` if successfully created
- `400` if incorrect data is provided
- `403` if user is not authenticated
- `409` if passenger with `phone` and `birthdate` exists for this trip


#### List all passengers

**GET:** `/api/v1/passenger/`

**NOTES:**
- This will return a list of all unique passengers

**Response:**
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 2,
      "user": 1,
      "trip": 1,
      "first_name": "Julian",
      "middle_name": "",
      "last_name": "Edelman",
      "gender": "M",
      "birthdate": "1111-11-11",
      "timestamp": "2016-02-29T18:26:52.413471Z"
    },
    {
      "id": 1,
      "user": 1,
      "trip": 1,
      "first_name": "Rob",
      "middle_name": "",
      "last_name": "Gronk",
      "gender": "M",
      "birthdate": "1111-11-11",
      "timestamp": "2016-02-29T18:25:31.177351Z"
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
    "id": 1,
    "user": 1,
    "trip": 1,
    "first_name": "Rob",
    "middle_name": "",
    "last_name": "Gronk",
    "gender": "M",
    "birthdate": "1111-11-11",
    "timestamp": "2016-02-29T18:25:31.177351Z"
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
    "middle_name": "Monster"
}
```

**Response:**
```json
{
    "id": 1,
    "user": 1,
    "trip": 1,
    "first_name": "Rob",
    "middle_name": "Monster",
    "last_name": "Gronk",
    "gender": "M",
    "birthdate": "1111-11-11",
    "timestamp": "2016-02-29T18:25:31.177351Z"
}
```

**Status Codes:**
- `200` if successful
- `400` if `trip`, `phone` and `birthdate` are not unique together
- `403` if user is not authorized or owner
- `404` if passenger is not found


### Trips

A trip is made up of all of the user's flights purchased at once. A trip can be one-way or round-trip and a trip must be domestic. Each trip instance has a status dict field. This field represents the current status of the trip as it goes through the booking, purchasing, ticketing process. Trips are booked with Sabre and will be ticketed through a local host agency.

**STATUSES:**
- `is_selected`: Defaults to true when a trip is initially created.
- `is_passenger_ready`: Becomes true after passenger information is completed.
- `is_available`: Becomes true after checking price and availability on Sabre.
- `is_purchased`: Becomes true after passenger successfully purchase ticket.
- `is_booked`: Becomes true after trip is successfully booked through Sabre.
- `is_ticketed`: Becomes true once ticketing is successful.


#### Create a trip

**POST:** `/api/v1/trip/`

**Notes:**
- `departure_date` is the date of trip departure in the format `YYYY-MM-DD`.
- `trip_option` is the Google QPX tripOption. The following trip example below is a round trip from Chicago ORD to Denver DEN departing on `2016-02-16` and returning on `2016-02-17`. IMPORTANT: `trip_option` must be a Google QPX tripOption and have `kind`, `id`, `slice` and `purchase` field. The value of `kind` must be `qpxexpress#tripOption`.

**Body:**
```json
{
    "departure_date": "2016-02-16",
    "trip_data": {
      "slice": [
        {
          "duration": 159,
          "segment": [
            {
              "id": "GRVECUxTw70vJ0tX",
              "duration": 159,
              "carrier": "NK",
              "number": "847",
              "cabin": "COACH",
              "booking_code": "Y",
              "booking_count": 1,
              "married": "0",
              "leg": [
                {
                  "id": "LcFy6BgTQAq1iHjZ",
                  "duration": 159,
                  "aircraft": "320",
                  "arrival_time": "2016-02-16T14:04-07:00",
                  "departure_time": "2016-02-16T12:25-06:00",
                  "origin": "ORD",
                  "destination": "DEN"
                }  
              ]
            }
          ]
        },
        {
          "duration": 151,
          "segment": [
            {
              "id": "G+kXUtDqIMFX4Z5l",
              "duration": 151,
              "carrier": "NK",
              "number": "630",
              "cabin": "COACH",
              "booking_code": "Y",
              "booking_count": 1,
              "married": "1",
              "leg": [
                {
                  "id": "LGe417zWHUYN3Oma",
                  "duration": 151,
                  "aircraft": "320",
                  "arrival_time": "2016-02-17T17:06-06:00",
                  "departure_time": "2016-02-17T13:35-07:00",
                  "origin": "DEN",
                  "destination": "ORD"
                }
              ]
            }
          ]
        }
      ]
    },
    "pricing_data": {
        "fare_total": "USD885.58",
        "tax_total": "USD111.62",
        "sale_total": "USD997.20",
        "latestTicketingTime": "2016-02-16T10:25-05:00",
        "ptc": "ADT",
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
        ],
        "tax": [
          {
            "code": "US",
            "chargeType": "GOVERNMENT",
            "country": "US",
            "id": "US_001",
            "salePrice": "USD18.01"
          },
          {
            "code": "AY",
            "chargeType": "GOVERNMENT",
            "country": "US",
            "id": "AY_001",
            "salePrice": "USD11.20"
          },
          {
            "code": "XF",
            "chargeType": "GOVERNMENT",
            "country": "US",
            "id": "XF",
            "salePrice": "USD9.00"
          },
          {
            "code": "ZP",
            "chargeType": "GOVERNMENT",
            "country": "US",
            "id": "ZP",
            "salePrice": "USD8.00"
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
    "cheapest_price": 286.20,
    "status": {
      "is_selected": true,
      "is_passenger_ready": false,
      "is_available": false,
      "is_purchased": false,
      "is_booked": false,
      "is_ticketed": false,
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
        "is_passenger_ready": false,
        "is_available": false,
        "is_purchased": false,
        "is_booked": false,
        "is_ticketed": false,
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
        "is_passenger_ready": false,
        "is_available": false,
        "is_purchased": false,
        "is_booked": false,
        "is_ticketed": false,
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
      "is_passenger_ready": false,
      "is_available": false,
      "is_purchased": false,
      "is_booked": false,
      "is_ticketed": false,
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


#### Check trip availability

**GET:** `/api/v1/trip/availability/:id`

**Notes:**
- This route will check the flight availability through Sabre before the user enters their purchase info.
