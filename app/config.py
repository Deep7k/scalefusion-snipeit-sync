import os
from dotenv import load_dotenv

class Config:
    def __init__(self):
        load_dotenv()
        self.SECRET = os.getenv("SCALEFUSION_SECRET")
        self.SNIPEIT_URL = os.getenv("SNIPEIT_URL")
        self.SNIPEIT_API_KEY = os.getenv("SNIPEIT_API_KEY")
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
        self.FLASK_PORT = int(os.getenv("FLASK_PORT", 5000))

        # Validate required variables
        if not all([self.SECRET, self.SNIPEIT_URL, self.SNIPEIT_API_KEY]):
            raise ValueError("Missing required environment variables")

    def get_snipeit_headers(self):
        return {
            "Authorization": f"Bearer {self.SNIPEIT_API_KEY}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }