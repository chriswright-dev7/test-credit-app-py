# AppID Microservice

A Flask-based microservice that generates unique 14-digit application IDs and stores them with timestamps in a local JSON database.

---

## What It Does

- Exposes a `GET /appid` endpoint
- Generates a unique 14-digit App ID in format:

yyyymmddssnnnn

- Ensures no duplicate IDs
- Stores generated IDs with timestamps in a JSON file
- Uses safe (atomic) file writes to prevent corruption

---

## Run the Service


pip install flask python-dotenv
python AppId.py


Runs on:

http://localhost:5009


---

## Endpoint

### `GET /appid`

#### Response
```json id="appidres"
{
  "appId": "20260505123456",
  "timestamp": "2026-05-05T12:34:56"
}