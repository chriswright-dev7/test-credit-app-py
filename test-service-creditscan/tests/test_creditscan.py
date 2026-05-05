import unittest
import sys
import os
from unittest.mock import patch

# Add parent folder to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from test_service_creditscan import app, search_customer


class CreditScanTestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    # -----------------------------
    # 1. Test schema missing case
    # -----------------------------
    def test_schema_not_loaded(self):
        with patch('test_service_creditscan.schema', None):
            response = self.client.post('/creditscan', json={})

            self.assertEqual(response.status_code, 500)
            self.assertIn("Schema not loaded", response.get_json()["error"])

    # -----------------------------
    # 2. Test invalid JSON
    # -----------------------------
    def test_invalid_json(self):
        response = self.client.post(
            '/creditscan',
            data='{"bad_json": ',
            content_type="application/json"
        )

        self.assertIn(response.status_code, [400, 415])
        self.assertTrue(
            response.is_json is False or response.get_json() is None
        )

    # -----------------------------
    # 3. Test appid failure
    # -----------------------------
    @patch('test_service_creditscan.api_call_appid')
    @patch('test_service_creditscan.schema', {"type": "object"})
    def test_appid_failure(self, mock_appid):
        mock_appid.return_value = {"error": "appid service down"}

        payload = {
            "app": {
                "creditInfo": {
                    "firstName": "John",
                    "lastName": "Doe",
                    "SSN": "123",
                    "annualIncome": 60000
                }
            }
        }

        response = self.client.post('/creditscan', json=payload)

        self.assertEqual(response.status_code, 500)

    # -----------------------------
    # 4. Test no customer match
    # -----------------------------
    @patch('test_service_creditscan.search_customer')
    @patch('test_service_creditscan.api_call_appid')
    @patch('test_service_creditscan.schema', {"type": "object"})
    def test_no_match_found(self, mock_appid, mock_search):
        mock_appid.return_value = {"appId": "123"}
        mock_search.return_value = []

        payload = {
            "app": {
                "creditInfo": {
                    "firstName": "NoMatch",
                    "lastName": "User",
                    "SSN": "000",
                    "annualIncome": 60000
                }
            }
        }

        response = self.client.post('/creditscan', json=payload)

        self.assertEqual(response.status_code, 404)
        self.assertIn("No match found", response.get_json()["message"])

    # -----------------------------
    # 5. Test successful decision (AP)
    # -----------------------------
    @patch('test_service_creditscan.search_customer')
    @patch('test_service_creditscan.api_call_appid')
    @patch('test_service_creditscan.schema', {"type": "object"})
    def test_success_ap_decision(self, mock_appid, mock_search):
        mock_appid.return_value = {"appId": "999"}

        mock_search.return_value = [{
            "customerInfo": {
                "customerFirstName": "John",
                "customerLastName": "Doe",
                "customerSSN": "123"
            }
        }]

        payload = {
            "app": {
                "creditInfo": {
                    "firstName": "John",
                    "lastName": "Doe",
                    "SSN": "123",
                    "annualIncome": 60000
                }
            }
        }

        response = self.client.post('/creditscan', json=payload)

        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        self.assertEqual(data["app"]["appDecisionCode"], "AP")
        self.assertEqual(data["app"]["appId"], "999")

    # -----------------------------
    # 6. Test TD decision (low income)
    # -----------------------------
    @patch('test_service_creditscan.search_customer')
    @patch('test_service_creditscan.api_call_appid')
    @patch('test_service_creditscan.schema', {"type": "object"})
    def test_td_decision(self, mock_appid, mock_search):
        mock_appid.return_value = {"appId": "888"}

        mock_search.return_value = [{
            "customerInfo": {
                "customerFirstName": "Jane",
                "customerLastName": "Smith",
                "customerSSN": "999"
            }
        }]

        payload = {
            "app": {
                "creditInfo": {
                    "firstName": "Jane",
                    "lastName": "Smith",
                    "SSN": "999",
                    "annualIncome": 30000
                }
            }
        }

        response = self.client.post('/creditscan', json=payload)

        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        self.assertEqual(data["app"]["appDecisionCode"], "TD")


if __name__ == '__main__':
    unittest.main(verbosity=2)