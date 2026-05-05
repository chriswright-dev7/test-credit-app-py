# Sign-In Microservice

A Flask-based microservice that handles user authentication by validating credentials against data retrieved from the Customer Info service.

---

## What It Does

- Exposes a `POST /signin` API
- Accepts username and password
- Calls the Customer Info microservice to retrieve user data
- Validates credentials
- Returns authentication result

---

## Run the Service


pip install flask flask-cors
python signin.py


Runs on:

http://localhost:5001


---

## Endpoint

### `POST /signin`

#### Request
```json
{
  "username": "johndoe",
  "password": "password123"
}
Response (Success)
{
  "success": true,
  "user": { ... }
}
Response (Failure)
{
  "success": false,
  "message": "Invalid username or password."
}