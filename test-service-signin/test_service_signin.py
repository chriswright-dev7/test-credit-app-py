from urllib import request as urllib_request
from flask import Flask, request, jsonify
import json
from flask_cors import CORS

app = Flask(__name__)
host = 'localhost'
port = 5001
app_port = 5005
custinfo_port = 5002
CORS(app, origins=[f"http://{host}:{app_port}"])

# Call custinfo microservice
def api_search_custinfo(args):
    query = (args or '').replace(' ', '')

    try:
        response = urllib_request.urlopen(
            f"http://{host}:{custinfo_port}/custinfo?q={query}",
            data=json.dumps({}).encode('utf-8'),
            headers=
            {
                'Content-Type': 'application/json',
                "X-API-Key": "custinfo-secret"
            },
            method='GET'
        )
        return json.loads(response.read().decode('utf-8'))  # Return raw data instead of jsonify
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

    results = api_search_custinfo(username)
    # print("Search results:", results)

    user = next(
        (c for c in results if c["username"] == username and c["password"] == password),
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
    app.run(host=host, port=port)