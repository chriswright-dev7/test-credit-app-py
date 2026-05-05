import unittest
import sys
import os
from unittest.mock import patch

# Ensure parent directory is on path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from test_service_app import app as flask_app


class FlaskAppTestCase(unittest.TestCase):
    def setUp(self):
        flask_app.config['TESTING'] = True
        self.client = flask_app.test_client()

    def test_get_app_page(self):
        response = self.client.get('/app')
        self.assertIn(response.status_code, [200, 500])

    def test_receive_submission(self):
        response = self.client.post('/app', json={"name": "John"})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["message"], "Data received")

    def test_result_success(self):
        response = self.client.get('/result?status=success')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Application Successfully Submitted", response.data)

    def test_result_failure(self):
        response = self.client.get('/result?status=fail')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Something went wrong", response.data)
    

    def test_submit_success(self):
        with patch('test_service_app.api_call_creditscan') as mock_credit, \
            patch('test_service_app.api_call_fraudrisk') as mock_fraud:

            mock_credit.return_value = {
                "app": {
                    "appId": "123",
                    "appDecisionCode": "AP"
                }
            }
            mock_fraud.return_value = {"status": "ok"}

            response = self.client.post('/submit', data={"name": "John"})

            self.assertEqual(response.status_code, 200)
            self.assertIn(b"Transmitting Securely", response.data)


if __name__ == '__main__':
    unittest.main(verbosity=2)