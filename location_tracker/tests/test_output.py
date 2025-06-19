import unittest
from unittest.mock import patch
import os
from utils.output import generate_google_earth_link, save_json

class TestOutput(unittest.TestCase):
    def test_generate_google_earth_link(self):
        """Test generating Google Earth link."""
        latitude = 34.0549
        longitude = -118.2426
        link = generate_google_earth_link(latitude, longitude)
        
        expected = "https://earth.google.com/web/search/34.0549%2C-118.2426"
        self.assertEqual(link, expected)

    @patch("builtins.open")
    def test_save_json(self, mock_open):
        """Test saving data to JSON file."""
        data = [{"latitude": 34.0549, "longitude": -118.2426}]
        filename = "test.json"
        save_json(data, filename)
        
        mock_open.assert_called_with(filename, 'w')

    @patch("builtins.open", side_effect=IOError)
    def test_save_json_error(self, mock_open):
        """Test handling JSON save error."""
        data = [{"latitude": 34.0549, "longitude": -118.2426}]
        with self.assertRaises(IOError):
            save_json(data, "test.json")

if __name__ == "__main__":
    unittest.main()