# FraudRisk Microservice

A simple Flask-based microservice that evaluates fraud risk for credit applications using basic rules and schema validation.

---

## What It Does

- Exposes a `POST /fraudrisk` API
- Validates incoming requests using a JSON schema
- Applies simple rule-based fraud detection using last name
- Returns a fraud risk score and description

---

## Run the Service


pip install flask python-dotenv jsonschema
python fraudrisk.py


Runs on:

http://localhost:5004


---

## Endpoint

### `POST /fraudrisk`

#### Request
- JSON body required
- Must match `fraudrisk_request_schema.json`
