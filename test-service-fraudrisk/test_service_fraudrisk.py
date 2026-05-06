# fraudrisk.py


from dotenv import load_dotenv
from flask import Flask, request, jsonify
import os, json, sys
from jsonschema import validate, ValidationError

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from auth import require_api_key

# FRAUDRISK_KEY = "fraudrisk-secret"

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
SCHEMA_PATH = os.path.join(BASE_DIR, "fraudrisk_request_schema.json")

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


# API endpoint for fraudrisk
@app.route('/fraudrisk', methods=['POST'])
@require_api_key(FRAUDRISK_KEY)
def getFraudRisk():
    # Ensure schema is loaded
    if schema is None:
        return jsonify({"error": "Schema not loaded on server"}), 500

    # Get JSON safely
    data = request.get_json()
    # print("Received fraudrisk request:", data)

    if not data:
        print("Invalid or missing JSON body", data)
        return jsonify({"error": "Invalid or missing JSON body"}), 400

    # Validate request against schema
    error = validate_request(data, schema)
    if error:
        return jsonify({"error": error}), 400
    
    
    last_name = data.get("app", {}).get("creditInfo", {}).get("lastName", "")

    if last_name.lower() == "doe":
        return jsonify({"RiskScore": "9.1", "Description": "NO FRAUD DETECTED"})
    elif "fraud" in last_name.lower():
        return jsonify({"RiskScore": "2.5", "Description": "FRAUD DETECTED"})
    else:
        return jsonify({"RiskScore": "5.3", "Description": "CANNOT MATCH TO FRAUD DATABASE"})

if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=5004)
    app.run(host=HOST, port=fraudrisk_port, debug=True)