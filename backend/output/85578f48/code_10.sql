CREATE TABLE chat_messages (
    id SERIAL PRIMARY KEY,
    room_id VARCHAR(50),
    sender_id INTEGER REFERENCES users(id),
    receiver_id INTEGER REFERENCES users(id),
    message TEXT,
    message_type VARCHAR(20) DEFAULT 'text', -- text, emoji, image
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_read BOOLEAN DEFAULT FALSE
);