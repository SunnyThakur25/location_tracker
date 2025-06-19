import json
from urllib.parse import quote
from utils.logger import setup_logger

logger = setup_logger('output')

def generate_google_earth_link(latitude, longitude):
    """Generate Google Earth link for coordinates."""
    try:
        location = f"{latitude},{longitude}"
        encoded_location = quote(location)
        link = f"https://earth.google.com/web/search/{encoded_location}"
        logger.info(f"Generated Google Earth link: {link}")
        return link
    except Exception as e:
        logger.error(f"Error generating Google Earth link: {e}")
        return ""

def save_json(data, filename):
    """Save data to JSON file."""
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Saved JSON to {filename}")
    except Exception as e:
        logger.error(f"Error saving JSON: {e}")
        raise