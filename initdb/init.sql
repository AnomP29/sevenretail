CREATE TABLE IF NOT EXISTS leads (
    id SERIAL PRIMARY KEY,
    room_id VARCHAR(255) NOT NULL,
    channel VARCHAR(100),
    phone VARCHAR(50),
    booking_date DATE,
    transaction_date DATE,
    transaction_value INTEGER,
    funnel_keyword VARCHAR(100),
    lead_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
