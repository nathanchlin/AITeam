CREATE TABLE test_agent_performance (
    id VARCHAR(36) PRIMARY KEY,
    agent_id VARCHAR(36) NOT NULL,
    test_type VARCHAR(50) NOT NULL,
    success_rate DECIMAL(5,2),
    avg_response_time INT,
    total_tests INT,
    error_count INT,
    recorded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (agent_id) REFERENCES test_agents(id) ON DELETE CASCADE
);