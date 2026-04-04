# AITeam Backend

多 Agent 可视化协作系统的后端服务，基于 FastAPI + GLM-4/5 构建。

## 🎯 项目简介

AITeam Backend 是一个多 Agent 协作系统的后端 API 服务，提供：

- **Agent 管理**: 创建、配置、监控多个 AI Agent
- **任务编排**: Pipeline 队列管理，任务分配和执行
- **实时通信**: WebSocket 双向通信，实时推送 Agent 状态
- **代码生成**: 基于 GLM-5 的智能代码生成和合并
- **工作空间管理**: 每个 Agent 独立的工作空间和上下文
- **质量评估**: 代码质量评分和反馈系统

## 🏗️ 技术栈

### 核心框架
- **FastAPI** (0.109.0) - 现代 Python Web 框架
- **Uvicorn** (0.27.0) - ASGI 服务器
- **WebSockets** (12.0) - 实时双向通信

### 数据层
- **SQLAlchemy** (2.0.25) - ORM 框架
- **AIOSQLite** (0.19.0) - 异步 SQLite
- **Pydantic** (2.5.3) - 数据验证

### AI 能力
- **ZhipuAI** (2.0.1) - 智谱 AI SDK
- **GLM-4.7-Flash** - 通用对话模型
- **GLM-5.1** - 代码生成专用模型

### 任务队列（可选）
- **Celery** - 分布式任务队列
- **Redis** - 消息代理和结果存储

## 📦 安装

### 前置要求
- Python 3.11+
- SQLite 3
- GLM API Key (从 https://open.bigmodel.cn/ 获取)

### 快速开始

```bash
# 1. 克隆项目
cd ~/AITeam/backend

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的 GLM_API_KEY
```

### 环境变量配置

创建 `.env` 文件：

```env
# GLM API 配置
GLM_API_KEY=your_glm_api_key_here
GLM_MODEL=glm-4.7-flash
GLM_CODING_MODEL=glm-5.1

# 服务器配置
HOST=0.0.0.0
PORT=8000
DEBUG=true

# 数据库
DATABASE_URL=sqlite+aiosqlite:///./aiteam.db

# CORS (生产环境请设置具体域名)
CORS_ORIGINS=*

# Redis (可选，用于 Celery)
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
```

## 🚀 运行

### 开发模式

```bash
# 启动开发服务器（带热重载）
python -m app.main

# 或使用 uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 生产模式

```bash
# 使用 gunicorn + uvicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 启动 Celery Worker（可选）

```bash
# 启动异步任务队列
celery -A app.core.celery_app worker --loglevel=info
```

## 📚 API 文档

启动服务后访问：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **健康检查**: http://localhost:8000/health

## 🏛️ 项目结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 应用入口
│   ├── config.py            # 配置管理
│   ├── api/                 # API 路由
│   │   ├── agents.py        # Agent 管理 API
│   │   ├── tasks.py         # 任务管理 API
│   │   ├── pipeline.py      # Pipeline API
│   │   ├── projects.py      # 项目管理 API
│   │   ├── ws.py            # WebSocket 处理
│   │   └── group_chats.py   # 群聊 API
│   ├── agents/              # Agent 实现
│   │   ├── base.py          # Agent 基类
│   │   └── __init__.py
│   ├── services/            # 业务逻辑层
│   │   ├── agent_manager.py      # Agent 管理器
│   │   ├── coordinator.py        # Pipeline 协调器
│   │   ├── task_executor.py      # 任务执行器
│   │   ├── code_merger.py        # 代码合并服务
│   │   ├── workspace_manager.py  # 工作空间管理
│   │   ├── output_manager.py     # 输出管理
│   │   └── memory_service.py     # 记忆服务
│   ├── models/              # 数据模型
│   │   ├── schemas.py       # Pydantic 模型
│   │   └── __init__.py
│   ├── llm/                 # LLM 集成
│   │   ├── glm_client.py    # GLM API 客户端
│   │   └── __init__.py
│   ├── core/                # 核心功能
│   │   ├── celery_app.py    # Celery 配置
│   │   ├── tasks.py         # 异步任务
│   │   └── broadcast.py     # 广播服务
│   ├── middleware/          # 中间件
│   │   ├── error_handler.py # 错误处理
│   │   └── __init__.py
│   ├── tools/               # 工具集
│   ├── utils/               # 工具函数
│   └── data/                # 数据存储
│       └── workspaces/      # Agent 工作空间
├── requirements.txt         # Python 依赖
├── .env.example            # 环境变量示例
└── README.md               # 本文件
```

## 🤖 核心功能

### 1. Agent 管理

```python
# 创建 Agent
POST /api/agents
{
  "name": "CodeMaster",
  "type": "coder",
  "description": "专业代码开发专家",
  "custom_prompt": "...",
  "position": {"x": -4, "y": 0, "z": 0}
}

# Agent 类型
- coder: 代码开发
- analyst: 数据分析
- assistant: 助手协调
- tester: 测试工程
```

### 2. 任务执行

```python
# 创建任务
POST /api/tasks
{
  "title": "开发用户登录功能",
  "description": "实现 JWT 认证",
  "assigned_agent_id": "agent_001",
  "priority": "high"
}

# 任务状态流转
pending → in_progress → completed/failed
```

### 3. Pipeline 编排

```python
# 创建 Pipeline
POST /api/pipeline
{
  "name": "功能开发流程",
  "agents": ["coder", "tester"],
  "tasks": [
    {"title": "编码", "agent_type": "coder"},
    {"title": "测试", "agent_type": "tester"}
  ]
}
```

### 4. WebSocket 通信

```javascript
// 前端连接
const ws = new WebSocket('ws://localhost:8000/ws');

// 接收消息
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // 处理 Agent 状态更新、任务进度等
};

// 发送消息
ws.send(JSON.stringify({
  type: 'task_update',
  payload: {...}
}));
```

## 🔧 开发指南

### 添加新的 Agent 类型

1. 在 `app/models/schemas.py` 中添加类型枚举：

```python
class AgentType(str, Enum):
    coder = "coder"
    analyst = "analyst"
    custom = "custom"  # 新增类型
```

2. 在 `app/agents/` 中实现 Agent 类：

```python
from app.agents.base import BaseAgent

class CustomAgent(BaseAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = AgentType.custom
    
    async def execute_task(self, task):
        # 实现具体逻辑
        pass
```

### 添加新的 API 端点

1. 在 `app/api/` 创建路由文件：

```python
from fastapi import APIRouter

router = APIRouter(prefix="/custom", tags=["custom"])

@router.get("/")
async def custom_endpoint():
    return {"message": "Custom endpoint"}
```

2. 在 `app/main.py` 注册路由：

```python
from app.api import custom
app.include_router(custom.router, prefix="/api")
```

### 数据库迁移

```bash
# 创建迁移
alembic revision --autogenerate -m "描述"

# 执行迁移
alembic upgrade head
```

## 🧪 测试

```bash
# 运行测试
pytest tests/

# 带覆盖率报告
pytest --cov=app tests/
```

## 🐛 调试

### 日志

- **应用日志**: 查看控制台输出
- **Pipeline 日志**: `pipeline_debug.log`
- **Uvicorn 日志**: 自动输出到控制台

### 常见问题

1. **GLM API 调用失败**
   - 检查 `GLM_API_KEY` 是否正确
   - 检查网络连接
   - 查看速率限制

2. **数据库错误**
   - 删除 `aiteam.db` 重新创建
   - 检查文件权限

3. **WebSocket 连接失败**
   - 检查 CORS 配置
   - 确认前端地址在 `CORS_ORIGINS` 中

## 📝 License

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系方式

- GitHub: https://github.com/nathanchlin/AITeam
- Email: nathanchlin@gmail.com
