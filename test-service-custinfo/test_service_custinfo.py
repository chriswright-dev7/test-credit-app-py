# test_service_custinfo.py
# Flask microservice for customer info search

from dotenv import load_dotenv
from flask import Flask, request, jsonify
import os, json, sys
from flask_cors import CORS

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from auth import require_api_key

CUSTINFO_KEY = "custinfo-secret"

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

CORS(app, origins=[f"http://{HOST}:{cardapp_port}"])


# Load customer info data from JSON file
def load_custinfo():
    db_path = os.path.join(os.path.dirname(__file__), 'custinfo_db.json')
    with open(db_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# Search by firstName, lastName, CustomerNumber, or applicationId
def search_cust_info(query):
    query = query.lower()
    data = load_custinfo()
    results = []
    for cust in data:
        if (
            query in cust.get('firstName', '').lower() or
            query in cust.get('lastName', '').lower() or
            query in cust.get('CustomerNumber', '').lower() or
            query in cust.get('applicationId', '').lower() or
            query in cust.get('username', '').lower() or
            query in cust.get('password', '').lower()
        ):
            results.append(cust)
    return results

# API endpoint for customer info search
@app.route('/custinfo', methods=['GET'])
@require_api_key(CUSTINFO_KEY)
def api_search_custinfo():
    query = request.args.get('q', '')
    query = query.replace(' ', '')  # Remove spaces from the query string
    results = search_cust_info(query)
    print(f"Search query: {query}, Results: {results}")
    return jsonify(results)

if __name__ == '__main__':
    # port = int(os.environ.get('PORT', 3001))
    # host = os.environ.get('HOST', 'localhost')
    app.run(host=HOST, port=custinfo_port)

