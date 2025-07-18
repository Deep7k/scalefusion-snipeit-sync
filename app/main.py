from flask import Flask, request, abort
from dotenv import load_dotenv
import os
import hmac
import hashlib
import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime
import requests

# Load environment variables
load_dotenv()
SECRET = os.getenv("SCALEFUSION_SECRET")

# Set up logging
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
log_format = "%(asctime)s [%(levelname)s] %(message)s"

os.makedirs("logs", exist_ok=True)
log_filename = datetime.now().strftime("logs/assetsync-%Y%m%d.log")

# Set up TimedRotatingFileHandler to rotate daily
file_handler = TimedRotatingFileHandler(
    log_filename,
    when="midnight",
    interval=1,
    backupCount=7,  # Keep last 7 days
    encoding="utf-8"
)
file_handler.suffix = "%Y%m%d"
file_handler.setFormatter(logging.Formatter(log_format))

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter(log_format))

# Apply logging config
logging.basicConfig(
    level=getattr(logging, log_level),
    handlers=[console_handler, file_handler]
)

logger = logging.getLogger(__name__)

# Flask app setup
app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    raw_body = request.get_data()
    header_signature = request.headers.get("X-SF-Signature")

    logger.debug(f"🔒 Loaded SCALEFUSION_SECRET: {SECRET}")
    logger.debug(f"🔑 Incoming X-SF-Signature: {header_signature}")

    if not SECRET or not header_signature:
        logger.warning("Missing signature or secret")
        abort(400, "Missing signature or secret")

    computed_signature = hmac.new(
        SECRET.encode(),
        raw_body,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(header_signature, computed_signature):
        logger.error("❌ Signature mismatch!")
        abort(403, "Invalid signature")
    
    devices = data.get("data", {}).get("devices", [])
    for device in devices:
        sync_with_snipeit(device)

    data = request.json
    logger.info("✅ Verified webhook received:")
    logger.debug(data)
    logger.debug(f"Snipe-IT URL: {os.getenv('SNIPEIT_URL')}")

    return "OK", 200

def sync_with_snipeit(device):
    snipe_url = os.getenv("SNIPEIT_URL")
    api_token = os.getenv("SNIPEIT_API_KEY")
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    serial = device.get("serial_no")
    if not serial:
        logger.warning("⚠️ No serial number provided. Skipping sync.")
        return

    # Step 1: Try to find existing asset
    search_url = f"{snipe_url}/api/v1/hardware/byserial/{serial}"
    response = requests.get(search_url, headers=headers)

    if response.status_code == 200 and response.json().get("status") == "success":
        asset_id = response.json()["payload"]["id"]
        logger.info(f"🔁 Updating existing asset ID {asset_id} in Snipe-IT")

        update_data = {
            "model": device.get("model"),
            "manufacturer": device.get("make"),
            "serial": serial,
            "notes": f"Updated via webhook at {datetime.now().isoformat()}"
        }

        update_url = f"{snipe_url}/api/v1/hardware/{asset_id}"
        update_resp = requests.put(update_url, headers=headers, json=update_data)

        if update_resp.status_code == 200:
            logger.info("✅ Asset updated successfully.")
        else:
            logger.error(f"❌ Failed to update asset: {update_resp.text}")
    else:
        logger.info(f"➕ Asset not found. Optionally, create new asset with serial: {serial}")
        # Optional: implement create logic if needed

if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT", 5000))
    app.run(host="0.0.0.0", port=port)
