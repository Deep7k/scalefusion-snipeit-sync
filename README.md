## 📦 Flask Webhook Listener for Scalefusion + Snipe-IT

### 🔧 Overview

This is a lightweight Flask app designed to receive and verify webhooks from **Scalefusion**, optionally parse event data, and store it in a **PostgreSQL** database. It's intended to support further integration with **Snipe-IT** or internal tooling.

---

### 📁 Project Structure

```
scalefusion-snipeit-webhook/
├── app/
│   └── main.py            # Flask app
├── logs/                  # Auto-created daily rotating log files
├── .env                   # Environment config
├── requirements.txt       # Python dependencies
└── README.md              # This documentation
```

---

### ⚙️ Environment Configuration (`.env`)

Example:

```ini
# Flask config
FLASK_ENV=development
FLASK_PORT=5000

# Logging
LOG_LEVEL=DEBUG

# Scalefusion secret for HMAC verification
SCALEFUSION_SECRET=your_webhook_secret

# Snipe-IT (future use)
SNIPEIT_URL=your-snipeit-url

# PostgreSQL config
DB_ENABLED=true            # Toggle DB storage
DB_HOST=postgres
DB_PORT=5432
DB_NAME=your_db
DB_USER=your_user
DB_PASS=your_pass
```

---

### ▶️ Running the App

#### 🧪 Local (Python)

```bash
python3 app/main.py
```

The app will listen on `http://0.0.0.0:<FLASK_PORT>` and can receive POST requests at:

```
/webhook
```

#### 🌐 Expose with Cloudflared

```bash
cloudflared tunnel --url http://local-ip:5000 --hostname scalelistner.yourdomain.in
```

---

### 🔒 Webhook Security

* Webhook signatures are validated using HMAC-SHA256 with the shared `SCALEFUSION_SECRET`.
* Headers:

```
X-SF-Signature: <sha256>
```

---

### 🗃️ PostgreSQL Storage

If `DB_ENABLED=true`, the app will:

* Automatically create the table `webhook_events` (if missing).
* Insert parsed fields from the `device.reboot` webhook payload.

Schema:

```sql
CREATE TABLE webhook_events (
    id UUID PRIMARY KEY,
    event_type TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    model TEXT,
    make TEXT,
    serial_no TEXT,
    os_version TEXT
);
```

---

### 🧾 Logs

* Logs are stored in `logs/assetsync-YYYYMMDD.log`
* Rotated daily and preserved for 7 days.
* Console + file logging both enabled.

---

### 📌 To Do / Future Plans

* [ ] Map device serials to Snipe-IT and update assets
* [ ] Web frontend (React/Node)
* [ ] Docker support
* [ ] Unit tests and validation
