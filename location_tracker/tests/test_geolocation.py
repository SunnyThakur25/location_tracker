import unittest
from unittest.mock import patch
from web.app import app, link_mappings

class TestGeolocation(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        link_mappings.clear()

    def test_geolocation_capture_photo(self):
        link_id = "abc123"
        link_mappings["photos/abc123"] = link_id
        response = self.app.get("/track/abc123", headers={"Host": "test.com"})
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"triggerGeolocation", response.data)

    def test_save_location_valid(self):
        with patch("web.app.callback"):
            data = {"latitude": 34.0549, "longitude": -118.2426, "accuracy": 20.0}
            response = self.app.post("/save", json=data)
            
            self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
    unittest.main()