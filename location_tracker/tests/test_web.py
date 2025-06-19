import unittest
from unittest.mock import patch
from flask import Flask
from web.app import app, link_mappings

class TestFlaskServer(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        link_mappings.clear()

    def test_handle_masked_link_valid(self):
        link_id = "abc123"
        link_mappings["photos/abc123"] = link_id
        response = self.app.get("/photos/abc123")
        
        self.assertEqual(response.status_code, 302)
        self.assertIn("/track/abc123", response.location)

    def test_track_photo_page(self):
        link_id = "abc123"
        link_mappings["photos/abc123"] = link_id
        response = self.app.get("/track/abc123", headers={"Host": "test.com"})
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"https://test.com/static/js/capture.js", response.data)

    def test_save_location_valid(self):
        with patch("web.app.callback") as mock_callback:
            data = {"latitude": 34.0549, "longitude": -118.2426, "accuracy": 20.0}
            response = self.app.post("/save", json=data)
            
            self.assertEqual(response.status_code, 200)
            mock_callback.assert_called()

if __name__ == "__main__":
    unittest.main()