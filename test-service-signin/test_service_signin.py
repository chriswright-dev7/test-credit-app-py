from urllib import request as urllib_request
from flask import Flask, request, jsonify
import json,sys, os
from flask_cors import CORS

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

CORS(app, origins=[f"http://{HOST}:{cardapp_port}"])

# Call custinfo microservice
def api_search_custinfo(args):
    query = (args or '').replace(' ', '')

    try:
        req = urllib_request.Request(
            f"http://{HOST}:{custinfo_port}/custinfo?q={query}",
            method='GET',
            headers={
                "Content-Type": "application/json",
                "X-API-Key": "custinfo-secret"
            }
        )

        response = urllib_request.urlopen(req)
        return json.loads(response.read().decode('utf-8'))

    except Exception as e:
        return {"error": str(e)}


@app.route('/signin', methods=['POST'])
def signin():
    data = request.get_json() or {}
    # print("Received body:", data)

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({
            "success": False,
            "message": "Username and password required."
        }), 400

    # results = api_search_custinfo(username)
    results = api_search_custinfo(username)

    if isinstance(results, dict):
        results = results.get("data", [])

    user = next(
        (
            c for c in results
            if isinstance(c, dict)
            and c.get("username") == username
            and c.get("password") == password
        ),
        None
    )

    if user:
        print("Login successful for user:", username) #for debugging
        return jsonify({
            "success": True,
            "user": user
        })
    else:
        print("Login failed: invalid username or password") #for debugging
        return jsonify({
            "success": False,
            "message": "Invalid username or password."
        }), 401


if __name__ == '__main__':
    app.run(host=HOST, port=signin_port)