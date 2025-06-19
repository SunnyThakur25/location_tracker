import unittest
from utils.link_masker import generate_masked_link

class TestLinkMasker(unittest.TestCase):
    def test_generate_masked_link(self):
        link = generate_masked_link("test.com", "photo", "abc123")
        self.assertEqual(link, "https://test.com/photos/abc123")

    def test_generate_masked_link_video(self):
        link = generate_masked_link("test.com", "video", "xyz123")
        self.assertEqual(link, "https://test.com/videos/xyz123")

if __name__ == "__main__":
    unittest.main()