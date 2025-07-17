-- Webhook Events Table for Scalefusion Data
CREATE TABLE IF NOT EXISTS webhook_events (
    id UUID PRIMARY KEY,
    event_type TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    model TEXT,
    make TEXT,
    serial_no TEXT,
    os_version TEXT
);
