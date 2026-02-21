CREATE TABLE test_agent_capabilities (
    id VARCHAR(36) PRIMARY KEY,
    agent_id VARCHAR(36) NOT NULL,
    capability_type VARCHAR(50) NOT NULL,
    capability_details JSON NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (agent_id) REFERENCES test_agents(id) ON DELETE CASCADE,
    CONSTRAINT chk_capability_details CHECK JSON_VALID(capability_details)
);