import unittest
import sys
import os
from unittest.mock import patch

# Ensure parent directory is on path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from test_service_custinfo import app, search_cust_info


class CustInfoTestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    # -------------------------
    # Test 1: Flask endpoint
    # -------------------------
    def test_api_search_custinfo_returns_results(self):
        response = self.client.get('/custinfo?q=john')

        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        # response should be a list
        self.assertIsInstance(data, list)

    # -------------------------
    # Test 2: search function (mock DB)
    # -------------------------
    @patch('test_service_custinfo.load_custinfo')
    def test_search_cust_info_matches_firstname(self, mock_db):
        mock_db.return_value = [
            {
                "firstName": "John",
                "lastName": "Doe",
                "CustomerNumber": "123",
                "applicationId": "A1",
                "username": "jdoe",
                "password": "pass"
            }
        ]

        results = search_cust_info("john")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["firstName"], "John")

    # -------------------------
    # Test 3: search by last name
    # -------------------------
    @patch('test_service_custinfo.load_custinfo')
    def test_search_cust_info_lastname(self, mock_db):
        mock_db.return_value = [
            {
                "firstName": "Jane",
                "lastName": "Smith",
                "CustomerNumber": "999",
                "applicationId": "B2",
                "username": "jsmith",
                "password": "pass"
            }
        ]

        results = search_cust_info("smith")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["lastName"], "Smith")

    # -------------------------
    # Test 4: no match case
    # -------------------------
    @patch('test_service_custinfo.load_custinfo')
    def test_search_cust_info_no_match(self, mock_db):
        mock_db.return_value = [
            {
                "firstName": "Alice",
                "lastName": "Brown",
                "CustomerNumber": "111",
                "applicationId": "C3",
                "username": "abrown",
                "password": "pass"
            }
        ]

        results = search_cust_info("zzz")

        self.assertEqual(results, [])


if __name__ == '__main__':
    unittest.main(verbosity=2)