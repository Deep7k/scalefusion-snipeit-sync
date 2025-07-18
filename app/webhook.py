import hmac
import hashlib
from flask import Flask, request, abort
from typing import Dict
from .logger import setup_logger
from .snipeit import SnipeITClient
from .config import Config  # Add this import

def create_app(config: Config) -> Flask:  # Remove quotes around Config
    app = Flask(__name__)
    logger = setup_logger(config.LOG_LEVEL)
    snipeit_client = SnipeITClient(config.SNIPEIT_URL, config.SNIPEIT_API_KEY, logger)

    @app.route("/webhook", methods=["POST"])
    def webhook():
        raw_body = request.get_data()
        header_signature = request.headers.get("X-SF-Signature")

        logger.debug(f"🔒 Loaded SCALEFUSION_SECRET: {'*' * len(config.SECRET) if config.SECRET else 'None'}")
        logger.debug(f"🔑 Incoming X-SF-Signature: {header_signature}")

        if not config.SECRET or not header_signature:
            logger.warning("Missing signature or secret")
            abort(400, "Missing signature or secret")

        computed_signature = hmac.new(
            config.SECRET.encode(), raw_body, hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(header_signature, computed_signature):
            logger.error("❌ Signature mismatch!")
            abort(403, "Invalid signature")

        try:
            data = request.json
            logger.info("✅ Verified webhook received")
            logger.debug(f"Webhook data: {data}")

            event_type = data.get("event")
            devices = data.get("data", {}).get("devices", [])
            logger.debug(f"Received event_type: {event_type}, devices: {devices}")

            if event_type == "device.enrolled":
                for device in devices:
                    snipeit_client.sync_device(device)
            else:
                logger.debug(f"ℹ️ Ignoring event type: {event_type}")

            return "OK", 200

        except ValueError as e:
            logger.error(f"❌ Invalid JSON payload: {e}")
            abort(400, "Invalid JSON payload")

    return app