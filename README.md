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

#### Trips
- [Search for a trip](#search-for-a-trip)


## API Routes


### Register a new user

**POST:** `/api/v1/user/register`

**Body:**
```json
{
    "first_name": "Cam",
    "last_name": "Newton",
    "email": "test@test.com",
    "password": "password1",
    "is_verified": false,
    "timestamp": "2016-02-14T23:19:26.513620Z"
}
```

**Notes:**
- `email`: user's email address, must be unique (string)
- `password`: must be at least 8 chars with at least 1 number (string)

Registering a user will return a valid API auth token.

**Response:**
```json
{
    "id": 5,
    "first_name": "Cam",
    "last_name": "Newton",
    "email": "test@test.com",
    "token": "6ba2103f4ac8a9712ffb2a689b0e"
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
- `401` if email and/or password are incorrect


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
    "last_name": "Brady"
}
```

**Response:**
```json
{
    "id": 5,
    "first_name": "Tom",
    "last_name": "Brady",
    "email": "test@test.com",
    "is_verified": false,
    "timestamp": "2016-02-14T23:19:26.513620Z"
}
```

**Status Codes:**
- `200` if successful
- `400` if incorrect data is provided


### Search for a trip

**POST:** `/api/v1/trip/search`

**Body:**
```json
{
    "passengers": {
        "adultCount": 1,
        "childCount": 1,
        "infantInLapCount": 1,
        "infantInSeatCount": 1,
        "seniorCount": 1

    },
    "flights": [
        {   
            "origin": "ORD",
            "destination": "DEN",
            "date": "2016-09-19",
            "maxStops": 2,
            "maxConnectionDuration": 60,
            "preferredCabin": "COACH",
            "permittedDepartureTime": {
                "earliestTime": "22:00",
                "latestTime": "23:00"
            },
            "permittedCarrier": ["AA", "UA"],
            "prohibitedCarrier": ["XX", "YY"]
        },
        {
            "origin": "DEN",
            "destination": "ORD",
            "date": "2016-09-28"
        }
    ],
    "maxPrice": "USD400.00",
    "saleCountry": "US",
    "refundable": false,
    "solutions": 2
}
```

**Notes:**
- `passengers`: A dict containing the number of passenger types.
- `flgihts`: A list of flights that make up the itinerary of the trip. Generally, one-way trips are expressed using a list of length one, round trips of length two. An example of a length three trip would be: ORD->DEN, DEN->LAX, LAX->ORD.
- `origin`: Airport or city IATA designator of the origin.
- `destination`: Airport or city IATA designator of the destination.
- `date`: Departure date in `YYYY-MM-DD` format.
- `maxStops`: Max number of stops a traveler is willing to take.
- `maxConnectionDuration`: The longest connection time between two flights a traveler is willing to take in minutes.
- `preferredCabin`: Choices can be: `COACH`, `PREMIUM_COACH`, `BUSINESS` or `FIRST`.
- `permittedDepartureTime`: Dict containing `earliestTime` and `latestTime` in `HH:MM` format.
- `permittedCarrier` and `prohibitedCarrier` are both lists of 2-letter IATA airlines.
- `maxPrice`: The most a traveler is willing to pay and is specified in ISO-4217 format.
- `saleCountry`: IATA country code representing the point of sale.
- `refundable`: Boolean regarding whether the purchase is refundable.
- `solutions`: Integer representing the number of instances to return.

REQUIRED VALUES are at least one adult or senior passenger, an origin, a destination, and a date.

**Response:**
```json
{
 "trips": {
  "tripOption": [
   {
    "kind": "qpxexpress#tripOption",
    "saleTotal": "USD396.20",
    "id": "IcL4NFJLo6KTg30NEU0yVR001",
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
        "id": "GtqiKLYW0KmaidxP",
        "cabin": "COACH",
        "bookingCode": "Y",
        "bookingCodeCount": 4,
        "marriedSegmentGroup": "0",
        "leg": [
         {
          "kind": "qpxexpress#legInfo",
          "id": "LEi1gZroQKwSOHQD",
          "aircraft": "320",
          "arrivalTime": "2016-02-15T14:04-07:00",
          "departureTime": "2016-02-15T12:25-06:00",
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
        "id": "GFw-cDHkkmrtzA57",
        "cabin": "COACH",
        "bookingCode": "Y",
        "bookingCodeCount": 4,
        "marriedSegmentGroup": "1",
        "leg": [
         {
          "kind": "qpxexpress#legInfo",
          "id": "LjKIcOK25qqq4igQ",
          "aircraft": "320",
          "arrivalTime": "2016-02-16T17:06-06:00",
          "departureTime": "2016-02-16T13:35-07:00",
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
      "kind": "qpxexpress#pricingInfo",
      "baseFareTotal": "USD342.32",
      "saleFareTotal": "USD342.32",
      "saleTaxTotal": "USD53.88",
      "saleTotal": "USD396.20",
     }
    ]
   },
   {
    "kind": "qpxexpress#tripOption",
    "saleTotal": "USD772.20",
    "id": "IcL4NFJLo6KTg30NEU0yVR002",
    "slice": [
     {
      "kind": "qpxexpress#sliceInfo",
      "duration": 164,
      "segment": [
       {
        "kind": "qpxexpress#segmentInfo",
        "duration": 164,
        "flight": {
         "carrier": "UA",
         "number": "2015"
        },
        "id": "GLBMCb+xnbol7a6G",
        "cabin": "COACH",
        "bookingCode": "U",
        "bookingCodeCount": 9,
        "marriedSegmentGroup": "0",
        "leg": [
         {
          "kind": "qpxexpress#legInfo",
          "id": "LX86DsruW4u1YOMa",
          "aircraft": "320",
          "arrivalTime": "2016-02-16T00:14-07:00",
          "departureTime": "2016-02-15T22:30-06:00",
          "origin": "ORD",
          "destination": "DEN",
          "originTerminal": "1",
          "duration": 164,
          "onTimePerformance": 70,
          "mileage": 885,
          "meal": "Food and Beverages for Purchase",
          "secure": true
         }
        ]
       }
      ]
     },
     {
      "kind": "qpxexpress#sliceInfo",
      "duration": 149,
      "segment": [
       {
        "kind": "qpxexpress#segmentInfo",
        "duration": 149,
        "flight": {
         "carrier": "UA",
         "number": "830"
        },
        "id": "GL3yXZ8HBsMM24ea",
        "cabin": "COACH",
        "bookingCode": "U",
        "bookingCodeCount": 9,
        "marriedSegmentGroup": "1",
        "leg": [
         {
          "kind": "qpxexpress#legInfo",
          "id": "LDXizkdZLovU1L0a",
          "aircraft": "320",
          "arrivalTime": "2016-02-16T19:49-06:00",
          "departureTime": "2016-02-16T16:20-07:00",
          "origin": "DEN",
          "destination": "ORD",
          "destinationTerminal": "1",
          "duration": 149,
          "onTimePerformance": 80,
          "mileage": 885,
          "meal": "Food and Beverages for Purchase",
          "secure": true
         }
        ]
       }
      ]
     }
    ],
    "pricing": [
     {
      "kind": "qpxexpress#pricingInfo",
      "baseFareTotal": "USD692.10",
      "saleFareTotal": "USD692.10",
      "saleTaxTotal": "USD80.10",
      "saleTotal": "USD772.20",
      "refundable": true
     }
    ]
   }
  ]
 }
}
```

**Status Codes:**
- `200` if successful
- `400` if incorrect data is provided
