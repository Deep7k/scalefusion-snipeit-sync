from flask import Flask, request, abort
from dotenv import load_dotenv
import os
import hmac
import hashlib

# Load environment variables
load_dotenv()
SECRET = os.getenv("SCALEFUSION_SECRET")

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    # Get the raw body and the signature from header
    raw_body = request.get_data()
    header_signature = request.headers.get("X-SF-Signature")
    print(f"🔒 Loaded SCALEFUSION_SECRET: {SECRET}")
    print(f"🔑 Incoming X-SF-Signature: {header_signature}")

    if not SECRET or not header_signature:
        abort(400, "Missing signature or secret")

    # Compute HMAC-SHA256 using the secret
    computed_signature = hmac.new(
        SECRET.encode(),
        raw_body,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(header_signature, computed_signature):
        print("❌ Signature mismatch!")
        abort(403, "Invalid signature")

    # Signature is valid, parse the payload
    data = request.json
    print("✅ Verified webhook received:")
    print(data)
    print(f"Snipe-IT URL: {os.getenv('SNIPEIT_URL')}")

    return "OK", 200

if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT", 5000))
    app.run(host="0.0.0.0", port=port)
