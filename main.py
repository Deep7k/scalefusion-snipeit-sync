from app.config import Config
from app.webhook import create_app

if __name__ == "__main__":
    config = Config()
    app = create_app(config)
    app.run(host="0.0.0.0", port=config.FLASK_PORT)