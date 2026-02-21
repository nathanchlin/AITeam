CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    type VARCHAR(20) NOT NULL, -- purchase, reward, refund
    amount INTEGER NOT NULL,
    currency VARCHAR(10) DEFAULT 'coins',
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    reference_id VARCHAR(100) -- 订单ID或交易引用
);