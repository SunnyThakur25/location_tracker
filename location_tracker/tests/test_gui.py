import unittest
from unittest.mock import patch
import tkinter as tk
from location_tracker import LocationTrackerGUI
from config import DEFAULT_HOST, DEFAULT_PORT, DEFAULT_DOMAIN

class TestLocationTrackerGUI(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.app = LocationTrackerGUI(self.root)
        self.app.root.update()

    def tearDown(self):
        self.app.root.destroy()

    def test_initial_state(self):
        self.assertEqual(self.app.content_var.get(), "photo")
        self.assertEqual(self.app.host_var.get(), DEFAULT_HOST)
        self.assertEqual(self.app.port_var.get(), str(DEFAULT_PORT))
        self.assertEqual(self.app.domain_var.get(), DEFAULT_DOMAIN)
        self.assertEqual(self.app.status_var.get(), "Ready")

    @patch("location_tracker.threading.Thread")
    @patch("location_tracker.start_flask_server")
    def test_start_server_valid(self, mock_flask, mock_thread):
        self.app.content_var.set("video")
        self.app.host_var.set("0.0.0.0")
        self.app.port_var.set("5000")
        self.app.domain_var.set("test.com")
        self.app.start_server()
        
        self.assertTrue(mock_thread.called)
        self.assertTrue(mock_flask.called)
        self.assertIn("Server running", self.app.status_var.get())
        self.assertTrue(self.app.link_var.get().startswith("https://test.com/videos/"))

    @patch("location_tracker.messagebox")
    def test_start_server_no_domain(self, mock_messagebox):
        self.app.domain_var.set("")
        self.app.start_server()
        
        mock_messagebox.showerror.assert_called_with("Error", "Domain is required", parent=self.app.root)

    @patch("location_tracker.pyperclip")
    def test_copy_link(self, mock_pyperclip):
        self.app.link_var.set("https://test.com/videos/abc123")
        self.app.copy_link()
        
        mock_pyperclip.copy.assert_called_with("https://test.com/videos/abc123")
        self.assertEqual(self.app.status_var.get(), "Link copied")

    @patch("location_tracker.webbrowser")
    def test_open_link(self, mock_webbrowser):
        self.app.link_var.set("https://test.com/videos/abc123")
        self.app.link_entry.event_generate("<Button-1>")
        
        mock_webbrowser.open.assert_called_with("https://test.com/videos/abc123")

    def test_update_results(self):
        data = {
            "latitude": 34.0549,
            "longitude": -118.2426,
            "accuracy": 20.0,
            "timestamp": "2025-06-19T09:57:00Z",
            "google_earth_link": "https://earth.google.com/web/search/34.0549,-118.2426"
        }
        self.app.update_results(data)
        
        items = self.app.tree.get_children()
        self.assertEqual(len(items), 1)
        self.assertEqual(self.app.tree.item(items[0])["values"][0], 34.0549)

    @patch("location_tracker.filedialog")
    @patch("location_tracker.save_json")
    def test_save_results(self, mock_save_json, mock_filedialog):
        mock_filedialog.asksaveasfilename.return_value = "test.json"
        data = {"latitude": 34.0549, "longitude": -118.2426}
        self.app.captured_data = [data]
        self.app.save_results()
        
        mock_save_json.assert_called_with([data], "test.json")

if __name__ == "__main__":
    unittest.main()