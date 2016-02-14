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


## API Routes Table of Contents

#### Users & profiles
- [Register a new user](#register-a-new-user)
- [Login a user](#login-a-user)
- [Logout a user](#logout-a-user)
- [Get the user's profile](#get-the-user's-profile)
- [Update the user's profile](#get-the-user's-profile)


## API Routes

### Users & profiles

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


### Get the user's profile

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


### Update the user's profile

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
