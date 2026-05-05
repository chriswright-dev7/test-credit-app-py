# test-service-creditscan
# Credit Application Microservices System

A distributed Flask-based microservices system that simulates a credit card application pipeline. It includes services for authentication, customer lookup, credit decisioning, fraud detection, and application ID generation.

---

## System Overview

This project is composed of multiple independent microservices that work together:

- Authentication Service (Sign-in)
- Customer Info Service
- CreditScan Service (Decision Engine)
- FraudRisk Service
- AppID Service
- Main Application Service

Each service runs independently and communicates over HTTP.

---

## Architecture


Frontend / Client
│
▼
Main App (Flask - port 5005)
│
┌──────┼──────────────┬───────────────┐
▼ ▼ ▼ ▼
Sign-in Customer Info CreditScan FraudRisk
(5001) (5002) (5003) (5004)
│
▼
AppID Service (5009)


---

## Services Summary

### 1. Sign-In Service (Port 5001)
- Authenticates users using username/password
- Calls Customer Info service
- Returns login success or failure

---

### 2. Customer Info Service (Port 5002)
- Searches customer database (`custinfo_db.json`)
- Supports search by name, customer number, application ID, etc.
- Returns matching customer records

---

### 3. CreditScan Service (Port 5003)
- Validates credit application using JSON schema
- Calls AppID service for unique application ID
- Searches decision database
- Applies credit decision logic:
  - Income > 50,000 → **Approve**
  - Otherwise → **Decline**
- Returns decision response

---

### 4. FraudRisk Service (Port 5004)
- Validates request using schema
- Applies rule-based fraud detection:
  - "doe" → No fraud
  - contains "fraud" → Fraud detected
  - otherwise → unknown risk
- Returns risk score and description

---

### 5. AppID Service (Port 5009)
- Generates unique 14-digit IDs (yyyymmddssnnnn format)
- Ensures no duplicates
- Stores IDs with timestamps in JSON DB
- Uses atomic file writes for safety

---

### 6. Main Application Service (Port 5005)
- Orchestrates full credit application flow
- Calls:
  - CreditScan
  - FraudRisk
- Combines results
- Stores final application in JSON database
- Redirects user to result page

---

## End-to-End Flow

1. User logs in via Sign-in service  
2. Customer data is validated  
3. User submits credit application  
4. Main service sends request to CreditScan  
5. CreditScan:
   - Validates schema
   - Calls AppID service
   - Applies credit decision logic  
6. FraudRisk evaluates fraud probability  
7. Main service aggregates:
   - Customer info
   - Credit decision
   - Fraud risk  
8. Final result is stored in database  
9. User sees application result page  

---

## Data Storage

Each service uses local JSON files:

| Service        | Database File |
|----------------|--------------|
| Customer Info  | custinfo_db.json |
| CreditScan     | creditscan_DecisionEngine_db.json |
| FraudRisk      | (schema-based, no persistent DB) |
| AppID          | appid_db.json |
| Main App       | credit_applications_db.json |

---

## Running the System

Install dependencies for each service:


pip install flask flask-cors python-dotenv jsonschema


Run services separately:


python AppId.py
python test_service_custinfo.py
python fraudrisk.py
python test_service_appid.py
python signin.py
python app.py


---

## 🔌 Default Ports

| Service        | Port |
|----------------|------|
| Main App       | 5005 |
| Sign-in        | 5001 |
| Customer Info  | 5002 |
| CreditScan     | 5003 |
| FraudRisk      | 5004 |
| AppID          | 5009 |

---

## API Key Authentication (auth.py)

The system includes a shared `auth.py` module to enforce **API key-based authentication between microservices**.

Each microservice protects endpoints like this:

Example (CreditScan)
from auth import require_api_key

CREDITSCAN_KEY = "creditscan-secret"

@app.route("/creditscan", methods=["POST"])
@require_api_key(CREDITSCAN_KEY)
def creditscan():
    ...
📡 Service-to-Service Calls

All internal HTTP requests must include the API key header:

headers={
    "Content-Type": "application/json",
    "X-API-Key": "creditscan-secret"
}


---

## 🧑‍💻 Author

Christopher D. Wright
---