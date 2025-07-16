from flask import Flask, request
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("📥 Webhook received:")
    print(data)
    
    # Example usage of env var
    print(f"Snipe-IT URL: {os.getenv('SNIPEIT_URL')}")

    return "OK", 200

if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT", 5000))
    app.run(host="0.0.0.0", port=port)
