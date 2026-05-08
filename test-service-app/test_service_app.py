from dotenv import load_dotenv
from urllib import request as urllib_request
from urllib.error import HTTPError
from flask import Flask, json, request, jsonify, send_from_directory, redirect, url_for
import os, uuid, sys
from flask_cors import CORS
import datetime


app = Flask(__name__, static_folder='public')
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

appId = None
decisionCode = None
sessionId = str(uuid.uuid4())

CORS(app, origins=[f"http://{HOST}:{cardapp_port}"])
@app.route("/config")
def config():
    return jsonify({
        "HOST": HOST,
        "SIGNIN_PORT": signin_port
    })

# -------------------------
# UI route (GET /app)
# -------------------------
@app.route('/app', methods=['GET'])
def serve_index():
    try:
        return app.send_static_file('index.html')
    except Exception as err:
        print('Error serving file:', err)
        return 'Error loading page', 500


# Call creditscan microservice
def api_call_creditscan(payload):
    try:
        req = urllib_request.Request(
            f"http://{HOST}:{creditscan_port}/creditscan",
            data=json.dumps(payload).encode('utf-8'),
            headers=
            {
                'Content-Type': 'application/json',
                "X-API-Key": "creditscan-secret"
            },
            method='POST'
        )

        response = urllib_request.urlopen(req)
        return json.loads(response.read().decode('utf-8'))

    except HTTPError as e:
        error_body = e.read().decode()
        raise RuntimeError(f"CreditScan HTTP {e.code}: {error_body}")

    except Exception as e:
        raise RuntimeError(f"CreditScan connection error: {e}")
    
# Call fraudrisk microservice
def api_call_fraudrisk(payload):
    try:
        req = urllib_request.Request(
            f"http://{HOST}:{fraudrisk_port}/fraudrisk",
            data=json.dumps(payload).encode('utf-8'),
            headers=
            {
                'Content-Type': 'application/json',
                "X-API-Key": "fraudrisk-secret"
            },

            method='POST'
        )

        response = urllib_request.urlopen(req)
        return json.loads(response.read().decode('utf-8'))

    except HTTPError as e:
        error_body = e.read().decode()
        raise RuntimeError(f"FraudRisk HTTP {e.code}: {error_body}")

    except Exception as e:
        raise RuntimeError(f"FraudRisk connection error: {e}")


# Save data to DB
def save_to_db(data):
    print("Saving data to DB:", data)
    db_path = os.path.join(os.path.dirname(__file__), "app_db", "credit_applications_db.json")

    try:
        # Load existing data
        if os.path.exists(db_path):
            with open(db_path, "r", encoding="utf-8") as f:
                db = json.load(f)
        else:
            db = []

        # db.append(data)
        db["applications"].append(data)

        # Write back
        with open(db_path, "w", encoding="utf-8") as f:
            json.dump(db, f, indent=2)
            print("Data saved to DB successfully.")

    except Exception as e:
        app.logger.error(f"Credit Application DB write failed: {e}")

# -------------------------
# API route SUBMIT (POST /app)
# -------------------------
@app.route('/app', methods=['POST'])
def receive_submission():
    data = request.get_json()

    print("Received submission:", data)

# Append data to JSON database
    try:
        with open('/app_db/credit_applications_db.json', 'r') as f:
            db = json.load(f)
    except FileNotFoundError:
        db = []
    
    # with open('credit_applications_db.json', 'a') as f:
    #     f.write(str(data) + '\n')

    return jsonify({
        "success": True,
        "message": "Data received"
    })


# submit route (POST /submit) to handle form submission and redirect to result page
@app.route('/submit', methods=['POST'])
def submit():
    global appId
    global decisionCode
    form_data = request.form.to_dict()
    # print("Form Data:", form_data)

    payload = {
        "app": {
            "creditInfo": form_data
        }
    }

    # Call CreditScan service
    # print("Calling THE CreditScan with payload:", payload)
    try:
        result_creditscan = api_call_creditscan(payload)
    except Exception as e:
        app.logger.error(f"CreditScan call failed: {e}")
        return jsonify({
            "error": "CreditScan Service Failure",
            "details": str(e)
        }), 500

    # print("CreditScan Response:", result_creditscan)
    # Only runs if no exception occurred
    app_data = result_creditscan.get("app", {})
    appId = app_data.get("appId")
    decisionCode = app_data.get("appDecisionCode")

    # Call FraudRisk service
    fraudrisk_payload = {
        "app": {
            "appId": appId,
            "sessionId": sessionId,
            "decisionCode": decisionCode,
            **payload.get("app", {})
        }
    }

    # print("FraudRisk Payload:", fraudrisk_payload)
    try:
        result_fraudrisk = api_call_fraudrisk(fraudrisk_payload)
    except Exception as e:
        app.logger.error(f"FraudRisk call failed: {e}")
        return jsonify({
            "error": "FraudRisk Service Failure",
            "details": str(e)
        }), 500

    # print("FraudRisk Response:", result_fraudrisk)

    #------------------
    # Save data to DB
    #------------------
    # Combine the custinfo, creditscan, and fraudrisk data
    response = {
        "app": {
            "contextId": sessionId,
            "timestamp": datetime.datetime.now().isoformat(),
            "custInfo": form_data,
            **result_creditscan.get("app", {}),
            "fraudInfo": result_fraudrisk
        }
    }
    # print("Final Response:", response)
    save_to_db(response)
        

    return """
    <html>
      <head>
        <meta http-equiv="refresh" content="2;url=/result?status=success">
      </head>
      <body style="text-align:center;margin-top:100px;">
        <h1>🔒 Transmitting Securely...</h1>
      </body>
    </html>
    """
    
# result page to display submission result
@app.route('/result')
def result():
    status = request.args.get("status")

    if status == "success":
        return """
        <html>
          <body style="text-align:center;margin-top:100px;">
            <h1 style="color:green;">✅ Application Successfully Submitted</h1>
            <br>
            <p><b>Application ID: """ + str(appId) + """</b></p>
            <p>Session ID: """ + str(sessionId) + """</p>
          </body>
        </html>
        """
    else:
        return """
        <html>
          <body style="text-align:center;margin-top:100px;">
            <h1 style="color:red;">❌ Something went wrong</h1>
            <br>
            <p>Session ID: """ + str(sessionId) + """</p>
          </body>
        </html>
        """

if __name__ == '__main__':
    # port = int(os.environ.get('PORT', 5005))
    # host = os.environ.get('HOST', 'localhost')
    app.run(host=HOST, port=cardapp_port, debug=True)