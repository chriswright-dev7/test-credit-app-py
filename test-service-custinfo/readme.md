# Customer Info Search Microservice

A simple Flask microservice that allows searching customer records from a local JSON file.

---

## What It Does

- Provides a `GET /custinfo` API endpoint
- Searches customer data by:
  - First name
  - Last name
  - Customer number
  - Application ID
  - Username
  - Password (demo only)
- Returns matching results as JSON

---

## Run the Service


pip install flask flask-cors python-dotenv
python test_service_custinfo.py


Access:

http://localhost:5002/custinfo?q=searchterm


---

## Endpoint

### `GET /custinfo?q=<query>`

- Case-insensitive search
- Removes spaces from query
- Returns matching customer records

---

## Data Source

- File: `custinfo_db.json`
- Stores customer records in JSON format
