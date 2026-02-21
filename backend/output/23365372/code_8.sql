CREATE TABLE test_agents (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    capabilities JSON NOT NULL,
    status ENUM('AVAILABLE', 'BUSY', 'OFFLINE', 'MAINTENANCE') NOT NULL DEFAULT 'AVAILABLE',
    location VARCHAR(100),
    tags JSON,
    metadata JSON,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_activity TIMESTAMP,
    performance_metrics JSON,
    CONSTRAINT chk_capabilities CHECK JSON_VALID(capabilities),
    CONSTRAINT chk_tags CHECK JSON_VALID(tags),
    CONSTRAINT chk_metadata CHECK JSON_VALID(metadata),
    CONSTRAINT chk_performance_metrics CHECK JSON_VALID(performance_metrics)
);