import unittest
import sys
import os
from unittest.mock import patch

from flask import request

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from test_service_fraudrisk import app


class FraudRiskTestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    # -----------------------------
    # 1. Schema missing test
    # -----------------------------
    def test_schema_not_loaded(self):
        with patch('test_service_fraudrisk.schema', None):
            response = self.client.post('/fraudrisk', json={})

            self.assertEqual(response.status_code, 500)
            self.assertIn("Schema not loaded", response.get_json()["error"])

    # -----------------------------
    # 2. Invalid JSON test
    # -----------------------------
    def test_invalid_json(self):
        response = self.client.post(
            '/fraudrisk',
            data='{"bad_json": ',
            content_type="application/json"
        )

        # Flask will return HTML 400
        self.assertEqual(response.status_code, 400)

        # DO NOT expect JSON
        self.assertIn(b"Bad Request", response.data)

    # -----------------------------
    # 3. Schema validation failure
    # -----------------------------
    def test_schema_validation_failure(self):
        payload = {
            "app": {
                "creditInfo": {
                    "lastName": 123   # invalid type likely triggers schema error
                }
            }
        }

        response = self.client.post('/fraudrisk', json=payload)

        self.assertEqual(response.status_code, 400)

        data = response.get_json()
        self.assertIn("error", data)

    # -----------------------------
    # 4. NO FRAUD DETECTED (Doe)
    # -----------------------------
    @patch('test_service_fraudrisk.schema', {"type": "object"})
    def test_no_fraud_detected(self):
        payload = {
            "app": {
                "creditInfo": {
                    "lastName": "Doe"
                }
            }
        }

        response = self.client.post('/fraudrisk', json=payload)

        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        self.assertEqual(data["RiskScore"], "9.1")
        self.assertEqual(data["Description"], "NO FRAUD DETECTED")

    # -----------------------------
    # 5. FRAUD DETECTED
    # -----------------------------
    @patch('test_service_fraudrisk.schema', {"type": "object"})
    def test_fraud_detected(self):
        payload = {
            "app": {
                "creditInfo": {
                    "lastName": "fraudster"
                }
            }
        }

        response = self.client.post('/fraudrisk', json=payload)

        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertIsNotNone(data)

        self.assertEqual(data["RiskScore"], "2.5")
        self.assertEqual(data["Description"], "FRAUD DETECTED")

    # -----------------------------
    # 6. DEFAULT CASE
    # -----------------------------
    @patch('test_service_fraudrisk.schema', {"type": "object"})
    def test_cannot_match_default(self):
        payload = {
            "app": {
                "creditInfo": {
                    "lastName": "Smith"
                }
            }
        }

        response = self.client.post('/fraudrisk', json=payload)

        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        self.assertEqual(data["RiskScore"], "5.3")
        self.assertEqual(data["Description"], "CANNOT MATCH TO FRAUD DATABASE")


if __name__ == '__main__':
    unittest.main(verbosity=2)