CREATE TABLE agents (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    host VARCHAR(100) NOT NULL,
    port INTEGER NOT NULL,
    status VARCHAR(20) CHECK (status IN ('online', 'offline', 'busy')),
    capabilities JSONB, -- 支持的测试类型和配置
    load INTEGER DEFAULT 0, -- 当前负载
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);