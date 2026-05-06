from dotenv import load_dotenv
from flask import Flask, request, jsonify
from urllib import request as urllib_request
from jsonschema import validate, ValidationError
import json, os, sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from auth import require_api_key


CREDITSCAN_KEY = "creditscan-secret"

load_dotenv()
app = Flask(__name__)
import settings
HOST = settings.CONFIG["HOST"]
cardapp_port = settings.CONFIG["CARDAPP_PORT"]
signin_port = settings.CONFIG["SIGNIN_PORT"]
custinfo_port = settings.CONFIG["CUSTINFO_PORT"]
creditscan_port = settings.CONFIG["CREDITSCAN_PORT"]
fraudrisk_port = settings.CONFIG["FRAUDRISK_PORT"]
appid_port = settings.CONFIG["APPID_PORT"]

CREDITSCAN_KEY = settings.CONFIG["CREDITSCAN_KEY"]
FRAUDRISK_KEY = settings.CONFIG["FRAUDRISK_KEY"]
APPID_KEY = settings.CONFIG["APPID_KEY"]
CUSTINFO_KEY = settings.CONFIG["CUSTINFO_KEY"]
SIGNIN_KEY = settings.CONFIG["SIGNIN_KEY"]

# -----------------------------
# Load schema at startup safely
# -----------------------------
schema = None
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCHEMA_PATH = os.path.join(BASE_DIR, "creditscan_request_schema.json")

try:
    with open(SCHEMA_PATH, "r") as f:
        schema = json.load(f)
        print("Schema loaded successfully")
except Exception as e:
    print("Schema load error:", e)


# -----------------------------
# Schema Validation Helper
# -----------------------------
def validate_request(data, schema):
    try:
        validate(instance=data, schema=schema)
        return None
    except ValidationError as e:
        return str(e)
    
# Call appid microservice
def api_call_appid():
    try:
        req = urllib_request.Request(
            f"http://{HOST}:{appid_port}/appid",
            headers={'Content-Type': 'application/json'},
            method='GET'
        )

        response = urllib_request.urlopen(req)
        return json.loads(response.read().decode('utf-8'))

    except Exception as e:
        return {"error": str(e)}

# -------------------------------------------------    
# Search decision DB for customers based on a query
# -------------------------------------------------
def search_customer(query):
    data = load_decision_data()
    results = []

    first_name = (query.get("firstName") or "").lower()
    last_name = (query.get("lastName") or "").lower()
    ssn = query.get("SSN") or ""

    for cust in data.get("Entities", []):
        info = cust.get("customerInfo", {})

        cust_first = (info.get("customerFirstName") or "").lower()
        cust_last = (info.get("customerLastName") or "").lower()
        cust_ssn = info.get("customerSSN") or ""

        if (
            (not first_name or first_name == cust_first) and
            (not last_name or last_name == cust_last) and
            (not ssn or ssn == cust_ssn)
        ):
            results.append(cust)
        # print("Decision Engine results:", results)
    return results

# Call Decision Data from JSON file
def load_decision_data():
    db_path = os.path.join(os.path.dirname(__file__), 'creditscan_DecisionEngine_db.json')
    with open(db_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# -----------------------------
# API endpoint
# -----------------------------
@app.route("/creditscan", methods=["POST"])
@require_api_key(CREDITSCAN_KEY)
def creditscan():
    # Ensure schema is loaded
    if schema is None:
        return jsonify({"error": "Schema not loaded on server"}), 500

    # Get JSON safely
    data = request.get_json()

    if not data:
        print("Invalid or missing JSON body", data)
        return jsonify({"error": "Invalid or missing JSON body"}), 400

    # Validate request against schema
    error = validate_request(data, schema)
    if error:
        return jsonify({"error": error}), 400

    # Safely extract nested data
    credit_info = data.get("app", {}).get("creditInfo", {})
    # print("Credit Info: ", credit_info)

    # Call appid microservice
    appid_data = api_call_appid()
    if "error" in appid_data:
        return jsonify({"error": appid_data["error"]}), 500
    appId = appid_data.get("appId")

    # -----------------------------
    # Decision logic - simulates decision engine
    # -----------------------------
    query = {
        "firstName": credit_info.get("firstName"),
        "lastName": credit_info.get("lastName"),
        "SSN": credit_info.get("SSN")
    }
    # print("Matches query: ", query)

    matches = search_customer(query)
    # print("Found Engine Match: ", matches)

    if not matches:
        return jsonify({"message": "No match found"}), 404
    
    # Assign the generated appId to the json object
    # matches[0]["appId"] = appId
    matches[0] = {
        "appId": appId,
        **matches[0]
    }
    # print("Matches with appId: ", matches)

    # Extract annual income and determine decision
    annual_income = float(credit_info.get("annualIncome") or 0)
    app_decision = "AP" if annual_income > 50000 else "TD"

    response = {
        "app": {
            "appId": appId,
            "appDecisionCode": app_decision,
            "appDecisionResponse": matches,
            **data.get("app", {})
        }
    }
    # print("final data with appId:", response)

    return jsonify(response)

# -----------------------------
# Run Server
# -----------------------------
if __name__ == "__main__":
    app.run(host=HOST, port=creditscan_port, debug=True)

