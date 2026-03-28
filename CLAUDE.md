# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AITeam is a Multi-Agent Visualization Collaboration System with a 3D interface. Users can create, manage, and collaborate with AI agents (Coder, Analyst, Assistant, Tester) on tasks through a pipeline system. The frontend uses React Three Fiber for 3D visualization, and the backend uses FastAPI with GLM-4/5 for LLM capabilities.

## Development Commands

### Backend
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Add GLM_API_KEY
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev  # http://localhost:5173
```

### Docker
```bash
docker-compose up -d
```

## Architecture

### Backend (FastAPI)

**Entry Point**: `backend/app/main.py` - Creates app, registers middleware, initializes default agents on startup

**Key Services**:
- `coordinator.py` - Central orchestration for multi-agent pipelines. Handles plan lifecycle (draft → discussing → approved → executing → completed), task execution with retry logic, and WebSocket broadcasting. Plans are persisted to `backend/data/plans.json`
- `agent_manager.py` - Factory and registry for agents. Creates agents by type with appropriate system prompts
- `output_manager.py` - File-based storage for generated outputs, with code consolidation for web apps

**Agent System** (`backend/app/agents/`):
- `BaseAgent` (abstract) - All agents implement `execute_task()` returning async generators for streaming responses, and `get_system_prompt()` for type-specific prompts
- Agent types: Coder (blue), Analyst (green), Assistant (purple), Tester (orange)
- CoderAgent enforces strict rules: no external file references, complete inline code, no Phaser/Three.js for games (Canvas only)

**LLM Integration** (`backend/app/llm/glm_client.py`):
- Streaming chat via async generators
- Handles GLM-4/5 API calls with zhipuai SDK

**Error Handling** (`backend/app/middleware/error_handler.py`, `backend/app/utils/exceptions.py`):
- Custom exception hierarchy (PlanNotFoundError, ValidationError, ExecutionError, etc.)
- Global exception handlers return structured JSON responses

### Frontend (React + TypeScript)

**Entry Point**: `frontend/src/App.tsx` - Wraps app in ErrorBoundary, renders 3D canvas with UI overlays

**State Management** (`frontend/src/stores/agentStore.ts`):
- Zustand store for agents, tasks, plans, WebSocket state
- `handleWebSocketMessage()` dispatches incoming messages by type

**3D Components** (`frontend/src/components/Scene/`):
- `World.tsx` - Main 3D scene with lighting, grid, and agent placement
- Agent characters with animations based on status (idle floating, working indicator)

**UI Components** (`frontend/src/components/UI/`):
- `PipelinePanel.tsx` - Multi-agent collaboration interface with discussion and task list
- `ChatPanel.tsx` - Agent chat with streaming responses and thinking process
- `Sidebar.tsx` - Agent list and creation

**WebSocket Hook** (`frontend/src/hooks/useWebSocket.ts`):
- Auto-reconnection with 3-second backoff
- Parses messages and updates Zustand store

## Pipeline Flow

1. **Create Plan** - User submits request via `/api/pipeline/start`
2. **Phase 1: Analyze** - Assistant analyzes requirements
3. **Phase 2: Discuss** - Selected agents provide input on the project
4. **Phase 3: Generate Plan** - Assistant creates task breakdown with agent assignments
5. **Phase 4: Execute** - Tasks run in order, with testing and fix iterations (max 3)

Plans persist to `backend/data/plans.json`. On server restart, the coordinator reloads plans and re-assigns agents (IDs may change).

## WebSocket Message Types

- `agent_update` - Agent status change
- `task_update` - Task progress
- `thinking` - Agent's step-by-step reasoning
- `stream` - Streaming content chunk
- `discussion` - New discussion message
- `plan_update` - Plan status change

## Key Patterns

- **Async Generators**: Used for streaming LLM responses - `async for chunk in agent.execute_task(task)`
- **WebSocket Broadcasting**: `await websocket_manager.broadcast(message)` sends to all clients
- **Task Retry**: Failed tasks retry up to 3 times with timeout (900s per task)
- **Web App Validation**: CoderAgent validates no external references, inline CSS/JS required
- **Pre-test Validation**: `output_manager.pre_test_validation()` checks generated code before testing phase

## Environment Variables

Backend `.env`:
```
GLM_API_KEY=required
GLM_MODEL=glm-5.1
DEBUG=true
```

## API Structure

- `/api/agents` - Agent CRUD
- `/api/tasks` - Task CRUD and execution
- `/api/pipeline/*` - Pipeline orchestration (start, resume, restart, plans)
- `/ws` - WebSocket endpoint

## PUA Skill 配置

本项目已集成 PUA Skill（`.claude/skills/pua/SKILL.md`），用于驱动 Claude 在复杂任务中穷尽一切方案。

**触发条件**：
- 任务连续失败 2 次以上
- AI 说 "我无法解决" / "建议手动处理"
- 在同一思路上原地打转（磨洋工）
- 用户表达沮丧："再试试"、"为什么还不行"

**手动触发**：输入 `/pua` 命令

**与 PUA Agent 配合**：
- Claude Code Skill 驱动 **开发时的 Claude**
- `PUACoderAgent` 等 Agent 类型驱动 **运行时的 AITeam Agent**

**AITeam Agent PUA 类型**：
- `pua-coder` - PUA 增强版代码开发专家
- `pua-analyst` - PUA 增强版数据分析师
- `pua-assistant` - PUA 增强版通用助手
- `pua-tester` - PUA 增强版测试专家

这些 Agent 在任务失败时会自动升级压力等级（L1-L4），通过 System Prompt 注入 PUA 方法论和话术。
