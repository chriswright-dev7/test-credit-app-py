# CreditScan Microservice

A Flask-based microservice that evaluates credit applications by validating input, querying a local decision dataset, generating an application ID, and returning a decision result.

---

## What It Does

- Exposes a `POST /creditscan` API
- Validates incoming requests using a JSON schema
- Calls an external AppID service to generate a unique application ID
- Searches a local decision dataset for customer matches
- Applies simple decision logic:
- Returns structured decision response

---

## Run the Service


pip install flask python-dotenv jsonschema
python app.py


Runs on:

http://localhost:5003


---

## Endpoint

### `POST /creditscan`

#### Request
- JSON body required
- Must match `creditscan_request_schema.json`


## Flow
Receive request
Validate against JSON schema
Call AppID service (/appid)
Search decision dataset for matching customer
Apply income-based decision logic
Return response with:
appId
decision code
matched customer data

## Data Sources
creditscan_request_schema.json → request validation
creditscan_DecisionEngine_db.json → customer decision data

## Notes
Returns 404 if no customer match is found
Returns 400 for invalid schema
Returns 500 if AppID service fails
Decision logic is simplified for demo purposes