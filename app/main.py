from flask import Flask, request, abort
from dotenv import load_dotenv
import os
import hmac
import hashlib
import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime
import psycopg2
from psycopg2.extras import execute_values

# Load environment variables
load_dotenv()
SECRET = os.getenv("SCALEFUSION_SECRET")
DB_ENABLED = os.getenv("DB_ENABLED", "false").lower() == "true"
DB_HOST = os.getenv("DB_HOST")       # from .env
DB_PORT = os.getenv("DB_PORT")       # from .env
DB_NAME = os.getenv("DB_NAME")       # from .env
DB_USER = os.getenv("DB_USER")       # from .env
DB_PASS = os.getenv("DB_PASS")       # from .env

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

    # ✅ Signature is valid, parse the payload
    data = request.json
    logger.info("✅ Verified webhook received:")
    logger.debug(data)

    event_id = data.get("id")
    event_type = data.get("event")
    created_at = data.get("created_at")
    devices = data.get("data", {}).get("devices", [])

    # ⬇️ Insert to DB if enabled
    if DB_ENABLED:
        for device in devices:
            insert_to_db(event_id, event_type, created_at, device)
    else:
        logger.debug("🛑 DB logging is disabled (DB_ENABLED=false)")

    logger.debug(f"Snipe-IT URL: {os.getenv('SNIPEIT_URL')}")  # Optional future use
    return "OK", 200

# New feature testing
def insert_to_db(event_id, event_type, created_at, device):
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS webhook_events (
                id UUID PRIMARY KEY,
                event_type TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL,
                model TEXT,
                make TEXT,
                serial_no TEXT,
                os_version TEXT
            )
        """)

        cursor.execute("""
            INSERT INTO webhook_events (id, event_type, created_at, model, make, serial_no, os_version)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, (
            event_id,
            event_type,
            created_at,
            device.get("model"),
            device.get("make"),
            device.get("serial_no"),
            device.get("os_version")
        ))

        conn.commit()
        cursor.close()
        conn.close()
        logger.info(f"📦 Inserted event {event_id} into DB")
    except Exception as e:
        logger.exception(f"❌ Failed to insert into DB: {e}")

if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT", 5000))
    app.run(host="0.0.0.0", port=port)
