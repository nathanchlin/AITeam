# 数据库设计与API接口规划

**Agent**: coder

**Time**: 2026-02-18T14:11:46.617803

---

# 测试代理数据模型与API接口规划

## 一、数据模型设计

### 1. 测试代理实体 (TestAgent)

```sql
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
```

### 2. 测试代理能力模型 (TestAgentCapability)

```sql
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
```

### 3. 测试代理性能记录 (TestAgentPerformance)

```sql
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
```

## 二、API接口规范

### 1. 代理注册接口

**接口名称**: `POST /api/v1/test-agents/register`

**功能描述**: 注册新的测试代理

**请求体**:
```json
{
    "name": "string",
    "description": "string",
    "capabilities": [
        {
            "type": "string",
            "details": {}
        }
    ],
    "location": "string",
    "tags": ["string"],
    "metadata": {}
}
```

**响应**:
```json
{
    "status": "success",
    "data": {
        "id": "uuid",
        "name": "string",
        "registered_at": "timestamp"
    }
}
```

### 2. 代理状态更新接口

**接口名称**: `PUT /api/v1/test-agents/{agentId}/status`

**功能描述**: 更新测试代理状态

**路径参数**:
- `agentId`: 测试代理ID

**请求体**:
```json
{
    "status": "AVAILABLE|BUSY|OFFLINE|MAINTENANCE",
    "metadata": {}
}
```

**响应**:
```json
{
    "status": "success",
    "data": {
        "id": "uuid",
        "status": "string",
        "updated_at": "timestamp"
    }
}
```

### 3. 代理选择请求接口

**接口名称**: `POST /api/v1/test-agents/select`

**功能描述**: 根据条件选择合适的测试代理

**请求体**:
```json
{
    "required_capabilities": [
        {
            "type": "string",
            "details": {}
        }
    ],
    "preferred_tags": ["string"],
    "location": "string",
    "max_response_time": 1000,
    "exclude_busy": true
}
```

**响应**:
```json
{
    "status": "success",
    "data": {
        "agent_id": "uuid",
        "name": "string",
        "capabilities": [],
        "location": "string",
        "estimated_availability": "timestamp",
        "score": 0.95
    }
}
```

### 4. 获取代理详情接口

**接口名称**: `GET /api/v1/test-agents/{agentId}`

**功能描述**: 获取指定测试代理的详细信息

**路径参数**:
- `agentId`: 测试代理ID

**响应**:
```json
{
    "status": "success",
    "data": {
        "id": "uuid",
        "name": "string",
        "description": "string",
        "capabilities": [],
        "status": "AVAILABLE",
        "location": "string",
        "tags": [],
        "metadata": {},
        "performance_metrics": {},
        "created_at": "timestamp",
        "updated_at": "timestamp",
        "last_activity": "timestamp"
    }
}
```

### 5. 代理性能报告接口

**接口名称**: `POST /api/v1/test-agents/{agentId}/performance`

**功能描述**: 提交测试代理的性能数据

**路径参数**:
- `agentId`: 测试代理ID

**请求体**:
```json
{
    "test_type": "string",
    "success_rate": 95.5,
    "avg_response_time": 250,
    "total_tests": 100,
    "error_count": 5
}
```

**响应**:
```json
{
    "status": "success",
    "data": {
        "recorded_at": "timestamp"
    }
}
```

## 三、API安全考虑

1. **认证与授权**:
   - 所有API请求需要通过JWT进行身份验证
   - 管理员角色可以执行所有操作
   - 普通用户只能注册和更新自己的代理

2. **速率限制**:
   - 代理选择接口限制每分钟100次请求
   - 代理注册接口限制每小时10次请求

3. **输入验证**:
   - 所有输入参数都需要进行严格验证
   - JSON格式数据需要验证其结构和内容

## 四、扩展考虑

1. **批量操作支持**:
   - 支持批量获取代理信息
   - 支持批量更新代理状态

2. **事件通知**:
   - 代理状态变更事件
   - 代理性能异常事件

3. **缓存策略**:
   - 热门代理信息缓存
   - 性能数据短期缓存

这个设计提供了完整的测试代理数据模型和API接口规范，支持代理的注册、状态管理、选择和性能跟踪等功能。根据实际需求，可以进一步扩展或调整这些接口。