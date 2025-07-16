from flask import Flask, request, abort
from dotenv import load_dotenv
import os
import hmac
import hashlib
import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime

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

    data = request.json
    logger.info("✅ Verified webhook received:")
    logger.debug(data)
    logger.debug(f"Snipe-IT URL: {os.getenv('SNIPEIT_URL')}")

    return "OK", 200

if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT", 5000))
    app.run(host="0.0.0.0", port=port)
