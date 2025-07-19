# ScaleFusion-SnipeIT Webhook Integration

This project provides a Flask-based webhook service that integrates ScaleFusion device enrollment events with Snipe-IT asset management. It listens for webhook events from ScaleFusion, verifies their authenticity, and synchronizes enrolled device data with Snipe-IT's asset inventory.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Setup](#setup)
  - [Environment Variables](#environment-variables)
  - [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Logging](#logging)
- [API Endpoints](#api-endpoints)
- [Error Handling](#error-handling)
- [Deployment](#deployment)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

## Overview
The webhook service receives device enrollment events from ScaleFusion, validates the payload using HMAC signatures, and synchronizes device details (e.g., asset tag, serial number, model, and manufacturer) with Snipe-IT via its API. The application is containerized using Docker and logs events for debugging and monitoring.

## Features
- **Webhook Verification**: Validates incoming ScaleFusion webhooks using HMAC-SHA256 signatures.
- **Device Synchronization**: Automatically syncs enrolled devices to Snipe-IT, creating assets if they don't exist.
- **Dynamic Model Lookup**: Retrieves Snipe-IT model IDs based on device model and manufacturer.
- **Logging**: Comprehensive logging with rotation to both console and files.
- **Containerized Deployment**: Runs in a Docker container for easy deployment and scalability.
- **Configurable**: Uses environment variables for sensitive configurations.

## Prerequisites
- Python 3.12+
- Docker and Docker Compose
- ScaleFusion account with webhook support
- Snipe-IT instance with API access
- `.env` file with required environment variables

## Setup

### Environment Variables
Create a `.env` file in the project root with the following variables:

```env
SCALEFUSION_SECRET=<your-scalefusion-webhook-secret>
SNIPEIT_URL=<your-snipeit-instance-url>
SNIPEIT_API_KEY=<your-snipeit-api-key>
LOG_LEVEL=INFO
FLASK_PORT=5000
```

- `SCALEFUSION_SECRET`: Secret key for verifying ScaleFusion webhook signatures.
- `SNIPEIT_URL`: Base URL of your Snipe-IT instance (e.g., `https://your-snipeit.com`).
- `SNIPEIT_API_KEY`: API key for Snipe-IT.
- `LOG_LEVEL`: Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`). Default: `INFO`.
- `FLASK_PORT`: Port for the Flask app. Default: `5000`.

### Installation
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd scalefusion-snipeit-webhook
   ```

2. Ensure the `.env` file is configured.

3. Build and run the Docker container:
   ```bash
   docker-compose up --build
   ```

4. The webhook will be available at `http://<host>:5000/webhook`.

## Usage
1. Configure ScaleFusion to send webhook events to `http://<your-host>:5000/webhook` for device enrollment events.
2. Ensure your Snipe-IT instance is accessible and the API key is valid.
3. Monitor logs in the `logs/` directory or console for debugging.

When a device is enrolled in ScaleFusion, the webhook will:
- Verify the webhook signature.
- Extract device details (name, serial number, model, manufacturer).
- Check if the asset exists in Snipe-IT by asset tag.
- If not found, retrieve the model ID and create a new asset.

## Project Structure
```plaintext
.
├── app/
│   ├── __init__.py
│   ├── config.py          # Environment variable loading and configuration
│   ├── logger.py          # Logging setup with file rotation
│   ├── snipeit.py         # Snipe-IT API client for asset synchronization
│   └── webhook.py         # Flask app and webhook endpoint
├── main.py                # Application entry point
├── Dockerfile             # Docker image configuration
├── docker-compose.yaml    # Docker Compose configuration
├── requirements.txt       # Python dependencies
└── .env                   # Environment variables (not tracked)
```

## Configuration
The `Config` class in `app/config.py` loads environment variables and validates their presence. Modify `.env` to adjust settings like logging level or Flask port.

## Logging
- Logs are written to the `logs/` directory with daily rotation (7-day retention).
- Log format: `%(asctime)s [%(levelname)s] %(message)s`.
- Console output is also enabled for real-time monitoring.
- Log levels can be set via the `LOG_LEVEL` environment variable.

## API Endpoints
- **POST /webhook**
  - **Description**: Handles ScaleFusion webhook events.
  - **Request**: JSON payload with `event` (e.g., `device.enrolled`) and `data.devices` array.
  - **Headers**: `X-SF-Signature` for HMAC verification.
  - **Response**:
    - `200 OK`: Successful processing.
    - `400 Bad Request`: Invalid JSON or missing signature/secret.
    - `403 Forbidden`: Invalid signature.

## Error Handling
- Missing environment variables raise a `ValueError` on startup.
- Invalid webhook signatures return a 403 response.
- Malformed JSON payloads return a 400 response.
- Snipe-IT API errors are logged and skipped to prevent service interruption.
- Network issues are caught and logged without crashing the service.

## Deployment
- Use Docker Compose for local or production deployment.
- Ensure the host is accessible to ScaleFusion's webhook service.
- For production, consider:
  - A reverse proxy (e.g., Nginx) for HTTPS.
  - Monitoring and alerting for logs.
  - Scaling with a WSGI server like Gunicorn.

## Testing
1. Send a test webhook from ScaleFusion or use a tool like `curl`:
   ```bash
   curl -X POST http://localhost:5000/webhook \
   -H "X-SF-Signature: <computed-signature>" \
   -H "Content-Type: application/json" \
   -d '{"event": "device.enrolled", "data": {"devices": [{"name": "TEST001", "serial_no": "12345", "model": "iPhone 12", "make": "Apple"}]}}'
   ```
2. Check logs in `logs/assetsync-<date>.log` for details.
3. Verify assets in Snipe-IT's web interface.

## Contributing
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/your-feature`).
3. Commit changes (`git commit -m "Add your feature"`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a pull request.

## License
This project is licensed under the MIT License. See `LICENSE` for details.