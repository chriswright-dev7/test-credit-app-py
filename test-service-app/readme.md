# Credit Application App

A Flask-based web application that acts as a orchestrator that processes credit card applications by integrating with external microservices for creditscan and fraudrisk, then storing results in a local JSON database.

---

## Features

- Web UI for submitting credit applications
- Integration with:
  - CreditScan microservice (credit decisioning)
  - FraudRisk microservice (fraud detection)
- Local JSON-based persistence
- Session tracking with unique IDs
- Result page with application status
- CORS support for frontend integration

---

## Architecture Overview

Client (Browser)  
↓  
Flask App (this service)  
├── CreditScan Service (port 5003)  
└── FraudRisk Service (port 5004)  
↓  
Local JSON Database (`app_db/credit_applications_db.json`)

---

## Project Structure
├── app.py
├── public/
│ └── index.html
├── app_db/
│ └── credit_applications_db.json
├── .env
└── README.md

## Configuration

Environment variables are loaded using `python-dotenv`.

Example `.env` file:

## Getting Started

### 1. Install Dependencies
pip install flask flask-cors python-dotenv


### 2. Run the App
http://localhost:5005/app

---

## 📡 API Endpoints

### `GET /app`
Serves the frontend UI (`index.html`).

### `POST /app`
Receives JSON data and returns a success response (currently does not persist data).

### `POST /submit`
- Accepts form submission
- Calls CreditScan service
- Calls FraudRisk service
- Combines responses
- Saves result to JSON database
- Redirects to result page

### `GET /result`
Displays submission result.

Query parameters:
- `status=success` → success page
- otherwise → error page

---

## Data Flow

1. User submits form  
2. Flask app sends request to CreditScan  
3. Receives:
   - `appId`
   - `appDecisionCode`  
4. Sends enriched payload to FraudRisk  
5. Combines:
   - Customer input
   - CreditScan response
   - FraudRisk response  
6. Saves data to JSON database  
7. Redirects user to result page  

---

## Database

**File location:**

app_db/credit_applications_db.json
