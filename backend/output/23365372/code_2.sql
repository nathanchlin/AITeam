CREATE TABLE test_tasks (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    requirements JSONB, -- 测试需求描述
    assigned_agent_id INTEGER REFERENCES agents(id),
    status VARCHAR(20) CHECK (status IN ('pending', 'assigned', 'running', 'completed', 'failed')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE
);