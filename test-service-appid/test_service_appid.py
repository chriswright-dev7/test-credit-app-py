# AppId.py
# Generates a 14-digit number based on yyyymmddssnnnn format


# Standard library imports
from dotenv import load_dotenv # Load environment variables from a .env file
import datetime  # For timestamps and date formatting
import random    # For generating random numbers
import json      # For reading/writing JSON files
import os        # For file path operations
import sys       # For adding paths to the Python path
from flask import Flask, jsonify  # Flask for microservice
import tempfile
import shutil

load_dotenv()
# Initialize Flask app
app = Flask(__name__)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
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

# Generate a unique 14-digit appId in yyyymmddssnnnn format
# Checks against existing_ids to avoid duplicates
def generate_app_id(existing_ids=None):
    if existing_ids is None:
        existing_ids = set()
    while True:
        now = datetime.datetime.now()
        yyyy = str(now.year)
        mm = f"{now.month:02d}"
        dd = f"{now.day:02d}"
        ss = f"{now.second:02d}"
        nnnn = f"{random.randint(0, 9999):04d}"
        app_id = f"{yyyy}{mm}{dd}{ss}{nnnn}"
        if app_id not in existing_ids:
            return app_id


# API endpoint to get a new unique appId and timestamp
@app.route("/appid", methods=["GET"])
def get_app_id():
    now = datetime.datetime.now()

    db_path = os.path.join(os.path.dirname(__file__), "appid_db.json")

    existing_ids = set()
    db_data = {"appid": []}

    # -------------------------
    # Load existing data safely
    # -------------------------
    if os.path.exists(db_path):
        try:
            with open(db_path, "r", encoding="utf-8") as f:
                db_data = json.load(f)

                for entry in db_data.get("appid", []):
                    if "appId" in entry:
                        existing_ids.add(entry["appId"])

        except Exception:
            # fallback if file is corrupted
            db_data = {"appid": []}

    # -------------------------
    # Generate new ID
    # -------------------------
    new_appid = generate_app_id(existing_ids)

    new_entry = {
        "appId": new_appid,
        "timestamp": now.isoformat()
    }

    db_data.setdefault("appid", []).append(new_entry)

    # -------------------------
    # Safe write (atomic)
    # -------------------------
    try:
        dir_name = os.path.dirname(db_path)

        with tempfile.NamedTemporaryFile(
            mode="w",
            delete=False,
            dir=dir_name,
            encoding="utf-8"
        ) as tmp_file:
            json.dump(db_data, tmp_file, indent=2)
            temp_name = tmp_file.name

        # Atomic replace (prevents corruption)
        shutil.move(temp_name, db_path)

    except Exception as e:
        return jsonify({"error": f"Failed to write DB: {str(e)}"}), 500

    # -------------------------
    # Return response
    # -------------------------
    return jsonify(new_entry)


# Run the Flask app
if __name__ == "__main__":
    app.run(host=HOST, port=appid_port)
