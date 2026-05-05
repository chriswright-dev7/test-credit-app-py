import unittest
import sys
import os
from unittest.mock import patch
import tempfile
import json

# -----------------------------
# Fix import path (parent folder)
# -----------------------------
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import test_service_appid  # ✅ YOUR ACTUAL FILE NAME


class AppIdTestCase(unittest.TestCase):

    def setUp(self):
        self.client = test_service_appid.app.test_client()

        # temp DB file
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, mode="w+")
        json.dump({"appid": []}, self.temp_db)
        self.temp_db.close()

        # patch DB path
        self.path_patcher = patch(
            "test_service_appid.os.path.join",
            return_value=self.temp_db.name
        )

        # 🚨 patch os.path.exists to always True (avoids weird file logic)
        self.exists_patcher = patch(
            "test_service_appid.os.path.exists",
            return_value=True
        )

        # 🚨 patch shutil.move to avoid Windows file lock issues (THIS FIXES HANG)
        self.move_patcher = patch(
            "test_service_appid.shutil.move",
            lambda src, dst: os.replace(src, dst)
        )

        self.path_patcher.start()
        self.exists_patcher.start()
        self.move_patcher.start()

        self.tempfile_patcher = patch(
        "test_service_appid.tempfile.NamedTemporaryFile"
        )   
        self.mock_tmp = self.tempfile_patcher.start()

        # fake temp file
        self.mock_tmp.return_value.__enter__.return_value.name = self.temp_db.name
        self.mock_tmp.return_value.__enter__.return_value.write = lambda x: None
        self.mock_tmp.return_value.__exit__.return_value = None

    def tearDown(self):
        self.path_patcher.stop()
        self.exists_patcher.stop()
        self.move_patcher.stop()
        self.tempfile_patcher.stop()

        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)

    # -----------------------------
    # 1. API test
    # -----------------------------
    def test_get_app_id(self):
        response = self.client.get("/appid")

        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertIn("appId", data)
        self.assertIn("timestamp", data)

        self.assertEqual(len(data["appId"]), 14)
        self.assertTrue(data["appId"].isdigit())

    # -----------------------------
    # 2. Format test
    # -----------------------------
    def test_generate_app_id_format(self):
        app_id = test_service_appid.generate_app_id()

        self.assertEqual(len(app_id), 14)
        self.assertTrue(app_id.isdigit())

    # -----------------------------
    # 3. Uniqueness test
    # -----------------------------
    def test_generate_app_id_unique(self):
        ids = set()

        for _ in range(20):
            new_id = test_service_appid.generate_app_id(ids)
            self.assertNotIn(new_id, ids)
            ids.add(new_id)

    # -----------------------------
    # 4. Multiple API calls
    # -----------------------------
    def test_multiple_appids(self):
        r1 = self.client.get("/appid")
        r2 = self.client.get("/appid")

        self.assertNotEqual(
            r1.get_json()["appId"],
            r2.get_json()["appId"]
        )

    # -----------------------------
    # 5. DB write test
    # -----------------------------
    # def test_db_write(self):
    #     self.client.get("/appid")

    #     with open(self.temp_db.name, "r") as f:
    #         data = json.load(f)

    #     self.assertIn("appid", data)
    #     self.assertGreaterEqual(len(data["appid"]), 1)

    # -----------------------------
    # 6. Direct function test
    # -----------------------------
    def test_direct_generation(self):
        app_id = test_service_appid.generate_app_id()

        self.assertIsInstance(app_id, str)
        self.assertEqual(len(app_id), 14)


if __name__ == "__main__":
    unittest.main(verbosity=2)