CREATE TABLE test_results (
    id SERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES test_tasks(id),
    agent_id INTEGER REFERENCES agents(id),
    result_data JSONB, -- 测试结果数据
    execution_time FLOAT, -- 执行时间(秒)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);