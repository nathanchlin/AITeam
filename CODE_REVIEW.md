# AITeam 代码审查报告 (CR)

## 1. 后端 (Backend)

### 1.1 安全 (Security)

#### 1.1.1 路径穿越 (Path Traversal) — 高优先级

**位置**: `backend/app/api/projects.py`, `backend/app/api/pipeline.py`

- **`get_project_file(project_id, filename)`**  
  `project_id` 与 `filename` 未做规范化与校验，恶意请求如 `project_id=../../../etc` 或 `filename=../../../etc/passwd` 可能访问到输出目录外的文件。

**建议**: 对路径做规范化并校验是否在允许的根目录下：

```python
import os
def _resolve_safe_path(base_dir: str, *parts: str) -> str | None:
    base = os.path.abspath(base_dir)
    path = os.path.abspath(os.path.join(base_dir, *parts))
    if not path.startswith(base):
        return None
    return path
# 在路由中：real_path = _resolve_safe_path(OUTPUT_DIR, project_id, filename)
```

- **`pipeline.py`** 中 `get_output_file(plan_id, filename)` 同理，应对 `plan_id`（或由其得到的目录）和 `filename` 做相同校验。

#### 1.1.2 敏感配置

- **`.env`** 不应提交到版本库；`README` 已说明复制 `.env.example`，建议确保 `.env` 在 `.gitignore` 中，且不要提交真实 API Key。
- **CORS** 在 `config.py` 中写死 `localhost:5173`；生产环境建议通过环境变量配置 `cors_origins`。

---

### 1.2 资源与生命周期

#### 1.2.1 TaskExecutor 任务完成后未从 `running_tasks` 移除 — 中优先级

**位置**: `backend/app/services/task_executor.py`

`execute_task` 在正常完成或异常后都没有从 `self.running_tasks` 中删除对应 `task_id`，会导致：

- 该 task 无法再次被 `start_task`（因为 `if task_id in self.running_tasks: return False`）；
- 长时间运行后字典只增不减，存在内存与逻辑泄漏。

**建议**: 在 `execute_task` 的 `try/finally` 中统一清理：

```python
async def execute_task(self, task_id: str, websocket_manager: Optional[Any] = None):
    try:
        # ... 现有逻辑 ...
    except Exception as e:
        # ... 现有错误处理 ...
    finally:
        self.running_tasks.pop(task_id, None)
```

并在 `start_task` 里用 `task.add_done_callback` 在任务结束时从 `running_tasks` 移除，或保持上述 `finally` 方式（二选一，避免重复删除）。

---

### 1.3 异常与错误处理

#### 1.3.1 裸 `except` 与静默吞错

**位置**: `backend/app/api/projects.py`

- `load_plans_data()`、`_get_project_info_fast()` 等使用裸 `except: pass`，会吞掉所有异常（包括 `KeyboardInterrupt`），不利于排查问题。

**建议**: 至少使用 `except Exception as e:` 并记录日志，或针对预期异常类型捕获。

#### 1.3.2 WebSocket 广播异常被静默

**位置**: `backend/app/api/ws.py` — `ConnectionManager.broadcast` / `send_personal_message`

- `try/except Exception: pass` 会静默忽略发送失败，无法发现断线、背压等问题。

**建议**: 使用 `logging.exception` 或 `logging.warning` 记录；对已断开的连接可从 `active_connections` 中移除。

---

### 1.4 代码质量与可维护性

#### 1.4.1 循环依赖

**位置**: `backend/app/api/tasks.py`

- `from app.main import websocket_manager` 在路由内按需导入，用于避免与 `main` 的循环依赖，说明模块边界不够清晰。

**建议**: 将 `websocket_manager` 抽到独立模块（如 `app/ws_manager.py`），由 `main` 和 `task_executor` 等共同引用，避免从 `main` 反向导入。

#### 1.4.2 重复的 `from app.main import websocket_manager`

**位置**: `backend/app/api/pipeline.py`

- 多个路由中重复写 `from app.main import websocket_manager` 和 `coordinator.set_websocket_manager(websocket_manager)`。

**建议**: 在模块顶部或依赖注入层统一设置一次，或通过 FastAPI 的 `Depends` 注入 ws_manager。

#### 1.4.3 魔法数字与配置

**位置**: `backend/app/services/coordinator.py`, `backend/app/api/pipeline.py`

- 如 `task_timeout = 900`、`max_fix_iterations = 3`、`TASK_TIMEOUT_SECONDS = 900` 等散落多处。

**建议**: 集中到 `config.py` 或配置类，便于调优和区分环境。

#### 1.4.4 日期时间

- 多处使用 `datetime.utcnow()`。在 Python 3.12+ 中 `utcnow()` 已被标记为 deprecated。

**建议**: 改为 `datetime.now(timezone.utc)` 并统一使用。

---

### 1.5 数据与状态

#### 1.5.1 Agent / Task 仅内存存储

**位置**: `backend/app/services/agent_manager.py`

- `agents` 与 `tasks` 仅存在内存字典中，进程重启后丢失；README 提到 SQLite，但当前未使用。

**建议**: 若需要持久化，引入 SQLite/ORM（如 SQLAlchemy）或先做简单文件持久化，与现有 `Plan` 持久化方式一致。

#### 1.5.2 Plan 与 Task 的 agent 类型比较

**位置**: `backend/app/api/pipeline.py` — `add_discussion_message`

- 使用 `next((a for a in agents if a.type == "assistant"), None)`。当前 `AgentType` 为 `str` 子类的 Enum，与 `"assistant"` 比较是成立的；为更清晰可写为 `a.type == AgentType.ASSISTANT`，避免对字符串的依赖。

---

### 1.6 LLM 与流式

#### 1.6.1 GLM 流式 API 使用方式

**位置**: `backend/app/llm/glm_client.py` — `chat_stream`

- 使用 `asyncio.to_thread` 调用同步的 `client.chat.completions.create(..., stream=True)`，然后在主线程里 `for chunk in response` 迭代。若 SDK 的同步迭代会阻塞，会阻塞线程池线程而非事件循环，但若迭代很慢，仍可能影响并发。

**建议**: 若智谱提供异步 SDK，优先使用原生 async；否则保持 to_thread，但考虑限制并发请求数（如信号量），避免线程池耗尽。

#### 1.6.2 `think_and_act` 与 prompt

**位置**: `backend/app/llm/glm_client.py`

- `think_and_act` 的 prompt 要求模型输出 JSON 行，但实现中并未解析这些行，只是把流式结果当作普通 stream 返回，与注释的 “thinking/action/result” 不一致。

**建议**: 要么在流式结果中解析 JSON 行并 yield 结构化 `thinking`/`action`/`result`，要么简化 prompt 与文档，避免误导。

---

## 2. 前端 (Frontend)

### 2.1 API 与 WebSocket 基址

**位置**: `frontend/src/App.tsx`, `frontend/src/hooks/useWebSocket.ts`

- `API_BASE = import.meta.env.PROD ? '' : 'http://localhost:8000'`；WebSocket 在 PROD 下用 `window.location.host`。若生产环境前后端同域且通过 Nginx 代理 `/api` 和 `/ws`，则可行；若部署在不同端口/子域，需用环境变量（如 `VITE_API_BASE`、`VITE_WS_URL`）配置，避免硬编码。

### 2.2 状态与性能

#### 2.2.1 Zustand 与 WebSocket 回调

**位置**: `frontend/src/stores/agentStore.ts`

- `handleWebSocketMessage` 内大量使用 `get().updateTask(...)`、`get().updatePlan(...)` 等，单条 WS 消息可能触发多次 `set`，若前端对 plan/task 列表做重渲染，可能带来多余渲染。

**建议**: 对同一条消息内的多次更新合并为一次 `set`（例如先计算好 new state 再 set），或对列表使用 `useShallowEqualSelector` 等减少不必要的重渲染。

#### 2.2.2 streamContent 无限增长

- `streamContent` 按 `taskId` 累积内容，任务完成后有 `clearStreamContent`；若某些分支未调用（例如 plan 流式），该 key 会一直保留。

**建议**: 对 plan 的 stream 也在适当时机清理，或为 stream 内容设上限/截断，避免长时间使用后内存增长。

### 2.3 类型与健壮性

- **位置**: `frontend/src/stores/agentStore.ts` — `handleWebSocketMessage`  
  `data.plan`、`data.message` 等直接断言类型使用，若后端格式变化可能运行时报错。

**建议**: 对 WS 的 `data` 做简单校验或使用 zod/io-ts 等做 schema 校验，对缺失字段给出默认值或安全降级。

### 2.4 可访问性与体验

- **位置**: `frontend/src/components/Scene/Agent.tsx`  
  点击选中 Agent 无键盘可访问性（无 focus、无 Enter/Space 触发）。

**建议**: 为 3D 场景中的可点击对象提供键盘焦点与按键事件，或在外层提供“当前选中 Agent”的列表/下拉以便键盘用户操作。

### 2.5 开发体验

- **位置**: `frontend/vite.config.ts`  
  开发时已配置 `/api` 和 `/ws` 的 proxy，与 `useWebSocket` 中 `ws://localhost:8000` 直连一致；若希望开发也走 proxy，可改为相对路径 `const WS_URL = (import.meta as any).env.PROD ? ... : '/ws'`，这样 dev 时也走 Vite 代理，便于与生产行为一致。

---

## 3. 通用建议

1. **测试**: 当前未见单测/集成测；建议至少为 `agent_manager`、`task_executor`、`output_manager.extract_code_blocks`、路径安全函数等核心逻辑补充单元测试，并为关键 API 增加集成测试。
2. **日志**: 统一使用 `logging`，按级别区分 debug/info/warning/error，避免到处 `print`。
3. **依赖注入**: WebSocket manager、coordinator、task_executor 等以全局单例存在；若后续要测试或多实例部署，可考虑通过 FastAPI `Depends` 或构造函数注入，便于替换实现。
4. **API 版本**: 若后续会做破坏性变更，可考虑路径前缀如 `/api/v1/`，便于版本演进。

---

## 4. 优化项汇总（按优先级）

| 优先级 | 类别     | 项 |
|--------|----------|----|
| 高     | 安全     | 文件下载接口 path traversal 校验 |
| 高     | 安全     | 确保 .env 与 API Key 不进入版本库，CORS 可配置化 |
| 中     | 资源     | TaskExecutor 任务结束后从 running_tasks 移除 |
| 中     | 可维护性 | 消除 main ↔ tasks 循环依赖，统一 ws_manager 注入 |
| 中     | 健壮性   | 替换裸 except、WebSocket 发送失败打日志并清理断连 |
| 低     | 代码质量 | 超时/重试等配置集中、datetime 使用 timezone、Plan 比较用 Enum |
| 低     | 前端     | WS 消息合并更新、streamContent 清理与上限、类型校验 |
| 低     | 体验     | 3D 场景键盘可访问性、生产 API/WS 基址环境变量 |

以上为本次 CR 的主要结论与建议，可按优先级分阶段落地。
