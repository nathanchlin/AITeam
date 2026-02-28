import asyncio
import os
import re
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid
import json
from pathlib import Path
from app.services.agent_manager import agent_manager
from app.services.output_manager import output_manager
from app.services.code_merger import code_merger
from app.services.quality_scorer import quality_scorer
from app.services.feedback_store import feedback_store
from app.models.schemas import (
    AgentType, AgentStatus, TaskStatus, PlanStatus,
    Plan, PlanTask, PlanCreate, DiscussionMessage, IterationTask, IterationRound
)
from app.llm.glm_client import glm_client, glm_coding_client

# Storage path for plan persistence
PLANS_STORAGE_FILE = Path(__file__).parent.parent.parent / "data" / "plans.json"


class CoordinatorService:
    def __init__(self):
        self.plans: Dict[str, Plan] = {}
        self.websocket_manager = None
        self.broadcast_manager = None
        # 停止迭代标志：{plan_id: set(round_numbers)}
        self._stop_flags: Dict[str, set] = {}
        # Load persisted plans on initialization
        self._load_plans()

    def request_stop_iteration(self, plan_id: str, round_number: int):
        """请求停止指定迭代"""
        if plan_id not in self._stop_flags:
            self._stop_flags[plan_id] = set()
        self._stop_flags[plan_id].add(round_number)
        print(f"[Coordinator] Stop requested for iteration {plan_id}/{round_number}")

    def should_stop_iteration(self, plan_id: str, round_number: int) -> bool:
        """检查是否应该停止迭代"""
        return plan_id in self._stop_flags and round_number in self._stop_flags[plan_id]

    def clear_stop_flag(self, plan_id: str, round_number: int):
        """清除停止标志"""
        if plan_id in self._stop_flags and round_number in self._stop_flags[plan_id]:
            self._stop_flags[plan_id].discard(round_number)

    def _load_plans(self):
        """Load plans from persistent storage"""
        import shutil

        if not PLANS_STORAGE_FILE.exists():
            return

        try:
            with open(PLANS_STORAGE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for plan_id, plan_data in data.get('plans', {}).items():
                try:
                    # Convert tasks back to PlanTask objects
                    tasks = []
                    for task_data in plan_data.get('tasks', []):
                        tasks.append(PlanTask(**task_data))
                    plan_data['tasks'] = tasks

                    # Convert discussion back to DiscussionMessage objects
                    discussion = []
                    for msg_data in plan_data.get('discussion', []):
                        discussion.append(DiscussionMessage(**msg_data))
                    plan_data['discussion'] = discussion

                    # Convert iterations back to IterationRound objects
                    iterations = []
                    for iter_data in plan_data.get('iterations', []):
                        # Convert iteration tasks
                        iter_tasks = []
                        for task_data in iter_data.get('tasks', []):
                            iter_tasks.append(IterationTask(**task_data))
                        iter_data['tasks'] = iter_tasks

                        # Convert iteration discussion
                        iter_discussion = []
                        for msg_data in iter_data.get('discussion', []):
                            iter_discussion.append(DiscussionMessage(**msg_data))
                        iter_data['discussion'] = iter_discussion

                        # Parse datetime strings for iteration
                        if iter_data.get('created_at'):
                            iter_data['created_at'] = datetime.fromisoformat(iter_data['created_at'])
                        if iter_data.get('completed_at'):
                            iter_data['completed_at'] = datetime.fromisoformat(iter_data['completed_at'])

                        iterations.append(IterationRound(**iter_data))
                    plan_data['iterations'] = iterations

                    # Parse datetime strings
                    if plan_data.get('created_at'):
                        plan_data['created_at'] = datetime.fromisoformat(plan_data['created_at'])
                    if plan_data.get('updated_at'):
                        plan_data['updated_at'] = datetime.fromisoformat(plan_data['updated_at'])
                    if plan_data.get('started_at'):
                        plan_data['started_at'] = datetime.fromisoformat(plan_data['started_at'])
                    if plan_data.get('completed_at'):
                        plan_data['completed_at'] = datetime.fromisoformat(plan_data['completed_at'])

                    self.plans[plan_id] = Plan(**plan_data)

                    # Re-assign agents to tasks (agent IDs may have changed after restart)
                    self._reassign_agents(plan_id)

                except Exception as e:
                    print(f"[Coordinator] Error loading plan {plan_id}: {e}")
                    continue

            print(f"[Coordinator] Loaded {len(self.plans)} plans from storage")

            # Auto-fix plans that are stuck in 'executing' but all tasks completed
            fixed_count = 0
            for plan_id, plan in self.plans.items():
                if plan.status == PlanStatus.EXECUTING:
                    all_completed = all(t.status == TaskStatus.COMPLETED for t in plan.tasks)
                    if all_completed:
                        plan.status = PlanStatus.COMPLETED
                        plan.completed_at = datetime.utcnow()
                        fixed_count += 1
                        print(f"[Coordinator] Auto-fixed stuck plan: {plan.title[:30]}...")

            if fixed_count > 0:
                self._save_plans()
                print(f"[Coordinator] Auto-fixed {fixed_count} stuck plans")

        except json.JSONDecodeError as e:
            # Backup corrupted file and start fresh
            print(f"[Coordinator] JSON file corrupted: {e}")
            backup_file = PLANS_STORAGE_FILE.with_suffix('.json.corrupted')
            shutil.move(str(PLANS_STORAGE_FILE), str(backup_file))
            print(f"[Coordinator] Corrupted file backed up to {backup_file}")
        except Exception as e:
            print(f"[Coordinator] Error loading plans: {e}")

    def _reassign_agents(self, plan_id: str):
        """Re-assign agents to tasks after loading (agent IDs may have changed)"""
        plan = self.plans.get(plan_id)
        if not plan:
            return

        # Get current agents, respecting user's selection order
        all_agents = agent_manager.get_all_agents()

        # Get current agents by type, respecting selected_agent_ids order
        agents_by_type = {}
        if plan.selected_agent_ids:
            for agent_id in plan.selected_agent_ids:
                agent = next((a for a in all_agents if a.id == agent_id), None)
                if agent:
                    agent_type = agent.type.value if hasattr(agent.type, 'value') else str(agent.type)
                    if agent_type not in agents_by_type:
                        agents_by_type[agent_type] = agent
        else:
            for agent in all_agents:
                agent_type = agent.type.value if hasattr(agent.type, 'value') else str(agent.type)
                if agent_type not in agents_by_type:
                    agents_by_type[agent_type] = agent

        # Re-assign agents to tasks
        reassigned = 0
        for task in plan.tasks:
            if task.assigned_agent_type and task.assigned_agent_type in agents_by_type:
                agent = agents_by_type[task.assigned_agent_type]
                if task.assigned_agent_id != agent.id:
                    task.assigned_agent_id = agent.id
                    reassigned += 1

        if reassigned > 0:
            print(f"[Coordinator] Re-assigned {reassigned} agents for plan {plan_id[:8]}")
            self._save_plans()

    def _save_plans(self):
        """Save plans to persistent storage with atomic write"""
        import shutil

        def convert_datetime(obj):
            """Recursively convert datetime objects to ISO format strings"""
            if isinstance(obj, dict):
                return {k: convert_datetime(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_datetime(item) for item in obj]
            elif isinstance(obj, datetime):
                return obj.isoformat()
            return obj

        try:
            # Ensure directory exists
            PLANS_STORAGE_FILE.parent.mkdir(parents=True, exist_ok=True)

            # Convert plans to serializable format
            plans_data = {}
            for plan_id, plan in self.plans.items():
                plan_dict = plan.model_dump()
                # Recursively convert all datetime objects
                plan_dict = convert_datetime(plan_dict)
                plans_data[plan_id] = plan_dict

            # Atomic write: write to temp file first, then rename
            temp_file = PLANS_STORAGE_FILE.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump({'plans': plans_data, 'saved_at': datetime.utcnow().isoformat()}, f, ensure_ascii=False, indent=2)

            # Atomic rename
            shutil.move(str(temp_file), str(PLANS_STORAGE_FILE))

        except Exception as e:
            print(f"[Coordinator] Error saving plans: {e}")

    def set_websocket_manager(self, ws_manager):
        self.websocket_manager = ws_manager

    def set_broadcast_manager(self, broadcast_manager):
        """Set broadcast manager for cross-process communication."""
        self.broadcast_manager = broadcast_manager

    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to WebSocket clients (supports cross-process via Redis)."""
        # Use broadcast manager for cross-process communication (Celery workers)
        if self.broadcast_manager:
            await self.broadcast_manager.broadcast(message)
        # Fallback to direct WebSocket broadcast (same process)
        elif self.websocket_manager:
            await self.websocket_manager.broadcast(message)

    async def create_plan(
        self,
        request: str,
        target_output: str = "web-app",
        created_by_agent_id: Optional[str] = None,
        selected_agent_ids: Optional[List[str]] = None,
    ) -> Plan:
        """Create a new plan from a user request"""
        plan_id = str(uuid.uuid4())
        plan = Plan(
            id=plan_id,
            title=f"计划: {request[:50]}...",
            original_request=request,
            target_output=target_output,
            created_by_agent_id=created_by_agent_id,
            selected_agent_ids=selected_agent_ids or [],
            status=PlanStatus.DRAFT,
        )
        self.plans[plan_id] = plan
        self._save_plans()  # Persist plan
        return plan

    async def add_discussion_message(
        self,
        plan_id: str,
        agent_id: str,
        agent_name: str,
        agent_type: str,
        content: str,
        message_type: str = "comment",
        reply_to: Optional[str] = None,
    ) -> DiscussionMessage:
        """Add a message to the plan discussion"""
        plan = self.plans.get(plan_id)
        if not plan:
            raise ValueError(f"Plan {plan_id} not found")

        msg = DiscussionMessage(
            id=str(uuid.uuid4()),
            plan_id=plan_id,
            agent_id=agent_id,
            agent_name=agent_name,
            agent_type=agent_type,
            content=content,
            message_type=message_type,
            reply_to=reply_to,
        )
        plan.discussion.append(msg)
        plan.updated_at = datetime.utcnow()
        self._save_plans()  # Persist after adding message

        await self.broadcast({
            "type": "discussion",
            "data": {
                "plan_id": plan_id,
                "message": msg.model_dump(),
            }
        })

        return msg

    async def analyze_request(self, plan_id: str) -> str:
        """Phase 1: Assistant analyzes the user request"""
        plan = self.plans.get(plan_id)
        if not plan:
            return "Plan not found"

        # Find the Assistant agent
        all_agents = agent_manager.get_all_agents()
        print(f"[Coordinator] Found {len(all_agents)} agents: {[a.name for a in all_agents]}")

        assistant = None
        for agent in all_agents:
            if agent.type == AgentType.ASSISTANT:
                assistant = agent
                break

        if not assistant:
            print("[Coordinator] No Assistant agent found!")
            return "No Assistant agent found"

        print(f"[Coordinator] Using Assistant: {assistant.name}")
        assistant.update_status(AgentStatus.WORKING)

        # Add discussion message about analysis starting
        await self.add_discussion_message(
            plan_id, assistant.id, assistant.name, "assistant",
            f"我来分析一下需求：{plan.original_request}",
            "comment"
        )

        analysis_prompt = f"""请分析以下用户需求，并识别关键功能点：

用户需求：{plan.original_request}
目标输出：{plan.target_output}

请输出：
1. 需求分析（2-3句话概括）
2. 核心功能列表（每行一个功能）
3. 技术建议

保持简洁，不要输出代码。"""

        full_response = ""
        try:
            async for chunk in glm_client.chat_stream(analysis_prompt, "assistant"):
                full_response += chunk
                await self.broadcast({
                    "type": "stream",
                    "data": {
                        "plan_id": plan_id,
                        "agent_id": assistant.id,
                        "content": chunk,
                    }
                })
        except Exception as e:
            print(f"[Coordinator] Error in analyze_request: {e}")
            full_response = f"分析出错: {str(e)}"

        await self.add_discussion_message(
            plan_id, assistant.id, assistant.name, "assistant",
            full_response,
            "proposal"
        )

        assistant.update_status(AgentStatus.IDLE)
        return full_response

    async def organize_discussion(self, plan_id: str) -> str:
        """Phase 2: Organize discussion between agents"""
        plan = self.plans.get(plan_id)
        if not plan:
            return "Plan not found"

        plan.status = PlanStatus.DISCUSSING

        # Get selected agents or fall back to all available
        all_agents = agent_manager.get_all_agents()

        if plan.selected_agent_ids:
            # Use only selected agents
            selected_agents = [a for a in all_agents if a.id in plan.selected_agent_ids]
        else:
            # Fall back to all available agents
            selected_agents = all_agents

        if not selected_agents:
            return "No agents available for discussion"

        # Find assistant (or first agent if no assistant)
        assistant = next((a for a in selected_agents if a.type == AgentType.ASSISTANT), None)
        if not assistant:
            assistant = selected_agents[0]

        # Assistant initiates discussion
        await self.add_discussion_message(
            plan_id, assistant.id, assistant.name, assistant.type.value,
            f"各位，请针对这个项目发表你们的看法和建议。参与本次协作的Agent有: {', '.join([a.name for a in selected_agents])}",
            "question"
        )

        # Define prompts for different agent types
        agent_prompts = {
            AgentType.CODER: """作为代码开发专家，请针对以下项目需求给出你的技术建议：

需求：{request}

请简短说明：
1. 推荐的技术栈
2. 需要实现的核心模块
3. 预计的开发步骤（3-5步）

保持简洁，每项1-2句话。""",

            AgentType.ANALYST: """作为数据分析师，请针对以下项目给出你的分析：

需求：{request}

请简短说明：
1. 项目可行性评估
2. 潜在风险点
3. 性能考量

保持简洁，每项1-2句话。""",

            AgentType.TESTER: """作为测试工程师，请针对以下项目给出你的测试建议：

需求：{request}

请简短说明：
1. 需要测试的核心功能
2. 关键测试场景
3. 质量保证建议

保持简洁，每项1-2句话。""",

            AgentType.ASSISTANT: """作为项目助手，请针对以下项目给出你的建议：

需求：{request}

请简短说明：
1. 项目整体规划
2. 需要注意的事项
3. 预期成果

保持简洁，每项1-2句话。""",
        }

        # Let each selected agent (except assistant) participate
        for agent in selected_agents:
            if agent.id == assistant.id:
                continue  # Skip assistant, they already initiated

            agent.update_status(AgentStatus.WORKING)

            # Get prompt template for this agent type
            prompt_template = agent_prompts.get(agent.type)
            if not prompt_template:
                # Custom agent - use generic prompt
                prompt_template = f"""作为{agent.name}，请针对以下项目给出你的专业建议：

需求：{{request}}

请简短说明你的专业观点和建议。保持简洁。"""

            prompt = prompt_template.format(request=plan.original_request)

            # Use custom prompt if available
            if agent.custom_prompt:
                prompt = f"{agent.custom_prompt}\n\n{prompt}"

            response = ""
            try:
                async def _collect_response():
                    nonlocal response
                    async for chunk in glm_client.chat_stream(prompt, agent.type.value):
                        response += chunk
                await asyncio.wait_for(_collect_response(), timeout=90)
            except asyncio.TimeoutError:
                print(f"[Coordinator] organize_discussion agent {agent.name} timeout 90s, using fallback")
                response = f"(该 Agent 回复超时，已跳过。建议：{plan.original_request[:80]}…)"
            except Exception as e:
                print(f"[Coordinator] organize_discussion agent {agent.name} error: {e}")
                response = f"(回复出错: {str(e)[:100]})"

            await self.add_discussion_message(
                plan_id, agent.id, agent.name, agent.type.value,
                response,
                "proposal"
            )
            agent.update_status(AgentStatus.IDLE)

        # Assistant summarizes
        await self.add_discussion_message(
            plan_id, assistant.id, assistant.name, assistant.type.value,
            "感谢各位的建议。我来总结一下大家的意见，形成最终计划。",
            "comment"
        )

        return "Discussion completed"

    async def generate_plan(self, plan_id: str) -> Plan:
        """Phase 3: Generate detailed execution plan"""
        plan = self.plans.get(plan_id)
        if not plan:
            raise ValueError(f"Plan {plan_id} not found")

        # Get selected agents or fall back to all available
        all_agents = agent_manager.get_all_agents()

        if plan.selected_agent_ids:
            selected_agents = [a for a in all_agents if a.id in plan.selected_agent_ids]
        else:
            selected_agents = all_agents

        # Find assistant (or first agent if no assistant)
        assistant = next((a for a in selected_agents if a.type == AgentType.ASSISTANT), None)
        if not assistant and selected_agents:
            assistant = selected_agents[0]

        if not assistant:
            raise ValueError("No agent available to generate plan")

        # Build a map of agent types to agents for task assignment
        # 按 selected_agent_ids 的顺序构建，确保尊重用户的选择顺序
        agents_by_type = {}
        if plan.selected_agent_ids:
            # 按用户选择的顺序分配，第一个选择的 agent 优先
            for agent_id in plan.selected_agent_ids:
                agent = next((a for a in selected_agents if a.id == agent_id), None)
                if agent:
                    agent_type = agent.type.value if hasattr(agent.type, 'value') else str(agent.type)
                    if agent_type not in agents_by_type:
                        agents_by_type[agent_type] = agent
        else:
            # 兜底：按默认顺序
            for agent in selected_agents:
                agent_type = agent.type.value if hasattr(agent.type, 'value') else str(agent.type)
                if agent_type not in agents_by_type:
                    agents_by_type[agent_type] = agent

        assistant.update_status(AgentStatus.WORKING)

        # Compile discussion summary
        discussion_summary = "\n".join([
            f"[{msg.agent_name}]: {msg.content}"
            for msg in plan.discussion[-5:]  # Last 5 messages
        ])

        # Build available agent types string for prompt
        available_agent_types = list(agents_by_type.keys())
        agent_types_str = "/".join(available_agent_types)

        # Add constraints for web-app projects
        web_app_constraints = ""
        if plan.target_output == "web-app":
            web_app_constraints = """
⚠️ 重要约束（Web应用项目必须遵守）：
1. 只能生成单文件HTML应用（包含内联CSS和JavaScript），无需后端服务器
2. 禁止创建后端相关任务（如：数据库设计、API开发、服务器搭建、用户认证等）
3. 禁止使用Node.js特有功能（如require、module.exports、express、socket.io等）
4. 所有功能必须在浏览器中运行，使用原生Canvas/WebGL/DOM API
5. 如需数据存储，只能使用localStorage或sessionStorage
6. 如需多人功能，只能实现本地多人（同一设备轮流或分屏），不能实现网络对战
7. 任务数量控制在5-8个以内，聚焦核心功能实现

任务示例（正确）：
- "游戏界面与基础渲染" - 使用Canvas绘制游戏画面
- "玩家控制与移动逻辑" - 处理键盘/鼠标输入
- "碰撞检测与得分系统" - 游戏核心逻辑
- "UI界面与动画效果" - 界面美化

任务示例（错误，禁止）：
- "后端服务器搭建" ❌
- "数据库设计与连接" ❌
- "用户认证系统" ❌
- "实时同步模块" ❌
"""

        # Add constraints for Godot projects
        godot_constraints = ""
        if plan.target_output == "godot-game":
            godot_constraints = """
⚠️ 重要约束（Godot游戏项目必须遵守）：
1. 只能生成 GDScript (.gd) 脚本文件，禁止 C# 脚本
2. 禁止创建外部资源任务（图片、音频、字体等素材制作）
3. 所有图形必须通过代码绘制，使用 draw_rect、draw_circle 等方法
4. 必须使用触摸输入（InputEventScreenTouch），禁止键盘/鼠标
5. 屏幕尺寸固定为 720x1280 竖屏
6. 禁止使用 Godot 4.3 已知问题功能：PointLight2D、GPUParticles2D
7. 任务数量控制在 3-5 个，聚焦核心游戏逻辑

任务示例（正确）：
- "游戏主场景与循环" - 创建 main.tscn 和 main.gd
- "玩家控制与触摸输入" - 触摸移动玩家
- "游戏对象与碰撞检测" - 使用 Area2D

任务示例（错误，禁止）：
- "制作角色精灵图" ❌ (外部资源)
- "添加背景音乐" ❌ (外部资源)
- "3D建模" ❌ (外部资源)
"""

        plan_prompt = f"""基于以下讨论，请生成详细的执行计划：

原始需求：{plan.original_request}
目标输出：{plan.target_output}
{web_app_constraints}{godot_constraints}
讨论摘要：
{discussion_summary}

可用的Agent类型：{agent_types_str}

请以JSON格式输出执行计划，格式如下：
{{
  "title": "计划标题",
  "description": "计划描述",
  "tasks": [
    {{
      "title": "任务标题",
      "description": "任务描述",
      "assigned_agent_type": "{agent_types_str}其中之一",
      "order": 1
    }}
  ]
}}

确保任务按顺序排列，每个任务明确分配给合适的Agent（从可用的Agent类型中选择）。"""

        full_response = ""
        plan_generation_timeout = 90  # 计划生成最多 90 秒，超时用兜底任务，避免卡在“计划生成中”

        async def _stream_plan_response():
            nonlocal full_response
            async for chunk in glm_client.chat_stream(plan_prompt, "assistant"):
                full_response += chunk
            return full_response

        try:
            full_response = await asyncio.wait_for(_stream_plan_response(), timeout=plan_generation_timeout)
        except asyncio.TimeoutError:
            print(f"[Coordinator] generate_plan timeout after {plan_generation_timeout}s, using fallback plan")
            full_response = ""
        except Exception as e:
            print(f"[Coordinator] generate_plan LLM error: {e}")
            full_response = ""

        # Parse JSON from response（失败则用兜底计划，确保不会一直停在“等待计划生成”）
        try:
            if full_response and "{" in full_response and "}" in full_response:
                json_start = full_response.find("{")
                json_end = full_response.rfind("}") + 1
                json_str = full_response[json_start:json_end]
                plan_data = json.loads(json_str)

                plan.title = plan_data.get("title", plan.title)
                plan.description = plan_data.get("description", "")

                for i, task_data in enumerate(plan_data.get("tasks", [])):
                    agent_type_str = task_data.get("assigned_agent_type", "coder")
                    assigned_agent_id = agents_by_type.get(agent_type_str)
                    assigned_agent_id = assigned_agent_id.id if assigned_agent_id else None

                    plan.tasks.append(PlanTask(
                        id=str(uuid.uuid4()),
                        title=task_data.get("title", "未命名任务"),
                        description=task_data.get("description", ""),
                        assigned_agent_id=assigned_agent_id,
                        assigned_agent_type=agent_type_str,
                        order=i + 1,
                    ))
            else:
                raise ValueError("empty or invalid response")
        except Exception as e:
            print(f"[Coordinator] generate_plan parse error: {e}, using fallback plan")
            plan.description = plan.description or full_response or "(计划生成超时或解析失败，已使用兜底任务)"
            fallback_agent = agents_by_type.get("coder") or agents_by_type.get("assistant") or (selected_agents[0] if selected_agents else None)
            plan.tasks = [
                PlanTask(
                    id=str(uuid.uuid4()),
                    title="实现核心功能",
                    description=plan.original_request,
                    assigned_agent_id=fallback_agent.id if fallback_agent else None,
                    assigned_agent_type=fallback_agent.type.value if fallback_agent else "coder",
                    order=1,
                )
            ]

        plan.status = PlanStatus.PENDING_APPROVAL
        plan.updated_at = datetime.utcnow()
        self._save_plans()

        await self.broadcast({
            "type": "plan_pending_approval",
            "data": {
                "plan_id": plan_id,
                "plan": plan.model_dump(),
                "message": "计划已生成，请确认后开始执行"
            }
        })

        assistant.update_status(AgentStatus.IDLE)
        return plan

    def approve_plan(self, plan_id: str) -> Optional[Plan]:
        """用户确认计划"""
        plan = self.plans.get(plan_id)
        if not plan:
            return None

        plan.status = PlanStatus.APPROVED
        plan.updated_at = datetime.utcnow()
        self._save_plans()

        return plan

    def reject_plan(self, plan_id: str, feedback: str = "") -> Optional[Plan]:
        """用户拒绝计划，返回讨论阶段"""
        plan = self.plans.get(plan_id)
        if not plan:
            return None

        plan.status = PlanStatus.DISCUSSING
        plan.updated_at = datetime.utcnow()

        # 添加反馈到讨论
        if feedback:
            asyncio.create_task(self.add_discussion_message(
                plan_id=plan_id,
                agent_id="user",
                agent_name="用户",
                agent_type="assistant",
                content=f"反馈：{feedback}",
                message_type="comment",
            ))

        self._save_plans()
        return plan

    def approve_iteration_plan(self, plan_id: str, round_number: int) -> Optional[IterationRound]:
        """用户确认迭代计划"""
        plan = self.plans.get(plan_id)
        if not plan:
            return None

        for iteration in plan.iterations:
            if iteration.round_number == round_number:
                iteration.status = PlanStatus.APPROVED
                plan.updated_at = datetime.utcnow()
                self._save_plans()
                return iteration

        return None

    def reject_iteration_plan(self, plan_id: str, round_number: int, feedback: str = "") -> Optional[IterationRound]:
        """用户拒绝迭代计划，返回讨论阶段"""
        plan = self.plans.get(plan_id)
        if not plan:
            return None

        for iteration in plan.iterations:
            if iteration.round_number == round_number:
                iteration.status = PlanStatus.DISCUSSING
                plan.updated_at = datetime.utcnow()

                # 添加反馈到迭代讨论
                if feedback:
                    asyncio.create_task(self._add_iteration_discussion_message(
                        plan_id=plan_id,
                        round_number=round_number,
                        agent_id="user",
                        agent_name="用户",
                        agent_type="assistant",
                        content=f"反馈：{feedback}",
                        message_type="comment",
                    ))

                self._save_plans()
                return iteration

        return None

    async def execute_plan(self, plan_id: str) -> str:
        """Phase 4: Execute the plan step by step with testing and feedback loop"""
        plan = self.plans.get(plan_id)
        if not plan:
            return "Plan not found"

        # 防止卡住：将任何处于 RUNNING 的任务重置为 PENDING，便于恢复或重新执行
        for task in plan.tasks:
            if task.status == TaskStatus.RUNNING:
                task.status = TaskStatus.PENDING
        self._save_plans()

        plan.status = PlanStatus.EXECUTING
        plan.started_at = datetime.utcnow()
        self._save_plans()  # Persist status change

        # Post start message to group chat
        await self.add_discussion_message(
            plan_id=plan_id,
            agent_id="system",
            agent_name="系统",
            agent_type="assistant",
            content=f"🚀 开始执行计划：{plan.title}\n\n共有 {len(plan.tasks)} 个任务需要完成。",
            message_type="comment",
        )

        await self.broadcast({
            "type": "plan_update",
            "data": {
                "plan_id": plan_id,
                "status": "executing",
            }
        })

        # Sort tasks by order
        sorted_tasks = sorted(plan.tasks, key=lambda t: t.order)
        results = []
        max_fix_iterations = 3  # Maximum bug fix iterations
        fix_iteration = 0

        # Separate coding tasks and testing tasks
        # Testing tasks are tasks with 'test' in the title or assigned to tester type
        testing_tasks = [t for t in sorted_tasks if 'test' in t.title.lower() or t.assigned_agent_type == 'tester']
        coding_tasks = [t for t in sorted_tasks if t not in testing_tasks]

        # Track first coding task completion for incremental mode
        first_coding_task_completed = False
        # Check if index.html already exists (from previous execution)
        if plan.target_output == "web-app":
            existing_code = output_manager.read_existing_code(plan_id)
            if existing_code:
                first_coding_task_completed = True

        while fix_iteration < max_fix_iterations:
            # Execute coding tasks
            for task in coding_tasks:
                if task.status == TaskStatus.COMPLETED:
                    continue  # Skip already completed tasks

                if not task.assigned_agent_id:
                    continue

                agent = agent_manager.get_agent(task.assigned_agent_id)
                if not agent:
                    continue

                # Execute task with retry logic
                task_timeout = 900  # 15 minutes timeout per task
                max_task_retries = 3  # Max retries per task
                task_retry_count = 0
                task_success = False

                while task_retry_count < max_task_retries and not task_success:
                    # Post task start to group chat
                    retry_msg = f" (第 {task_retry_count + 1} 次尝试)" if task_retry_count > 0 else ""
                    await self.add_discussion_message(
                        plan_id=plan_id,
                        agent_id=agent.id,
                        agent_name=agent.name,
                        agent_type=agent.type.value,
                        content=f"📝 开始任务：{task.title}{retry_msg}",
                        message_type="comment",
                    )

                    # Update task status
                    task.status = TaskStatus.RUNNING

                    await self.broadcast({
                        "type": "plan_update",
                        "data": {
                            "plan_id": plan_id,
                            "task_id": task.id,
                            "status": "running",
                        }
                    })

                    # Create task description
                    fix_context = ""
                    if fix_iteration > 0:
                        # Get previous test results for context
                        test_results = [r for r in results if '测试' in r.get('task', '')]
                        if test_results:
                            fix_context = f"\n\n⚠️ 之前的测试发现问题，请修复以下问题：\n{test_results[-1].get('result', '')}"

                    # Build context from previously completed tasks
                    previous_tasks_context = ""
                    if results:
                        previous_tasks_context = "\n\n📚 之前任务的输出（请参考这些内容来完成任务）：\n"
                        for prev_result in results:
                            task_title = prev_result.get('task', '未知任务')
                            task_result = prev_result.get('result', '')
                            # Truncate very long results to avoid context overflow
                            if len(task_result) > 3000:
                                task_result = task_result[:3000] + "\n... (内容已截断)"
                            previous_tasks_context += f"\n---\n### 任务：{task_title}\n\n{task_result}\n"

                    # ===== Incremental Code Modification =====
                    # For web-app projects, read existing code and pass to agent
                    existing_code = None
                    incremental_mode = False

                    if plan.target_output == "web-app" and agent.type.value == "coder":
                        if first_coding_task_completed:
                            # Read existing index.html for incremental modification
                            existing_code = output_manager.read_existing_code(plan_id)
                            if existing_code:
                                incremental_mode = True
                                print(f"[Coordinator] Using incremental mode for task: {task.title} (existing code: {len(existing_code)} chars)")

                    # Add web-app specific instructions
                    web_app_instructions = ""
                    if plan.target_output == "web-app" and agent.type.value == "coder":
                        if incremental_mode:
                            web_app_instructions = """

⚠️ 增量修改模式（重要）：
- 当前已有一个可运行的 index.html，你需要在此基础上进行修改
- 保持现有功能的同时添加新功能或修复问题
- 输出完整的修改后的 HTML 代码（不是差异对比）
- 确保修改后的代码仍然是完整的单文件 HTML 应用"""
                        else:
                            web_app_instructions = """

⚠️ Web应用开发要求（必须全部满足，否则视为未完成任务）：
1. 生成完整的单文件 HTML（包含内联 CSS 和 JavaScript），打开即可运行。
2. 不要引用外部文件（如 js/xxx.js, css/xxx.css）。
3. 禁止只输出类骨架或伪代码：每个类的方法必须有可执行实现体，不能只有注释或空函数。
4. 必须包含：<canvas> 元素、getContext('2d')、requestAnimationFrame 游戏循环、window.onload 或 DOMContentLoaded 初始化、键盘/鼠标事件绑定。
5. 若本计划中有多个任务分别产出模块（如 code_1.js 与 code_2.js），你负责的 HTML 应把所需逻辑整合进同一文件，确保最终 index.html 可独立运行，不依赖同目录其他 .js 文件。

🚫 禁止使用外部游戏框架（Phaser、Pixi.js、Three.js等）
✅ 只能使用原生 Canvas API 进行游戏开发"""

                    # Add Godot-specific instructions
                    godot_instructions = ""
                    if plan.target_output == "godot-game" and agent.type.value == "coder":
                        godot_instructions = """

⚠️ Godot 游戏开发要求（必须全部满足）：
1. 输出格式：每个文件用 `# filename: path/to/file.gd` 标注
2. 必须包含 project.godot、main.tscn、main.gd 等核心文件
3. 只使用 GDScript，禁止 C#
4. 所有图形用代码绘制（_draw() 方法）
5. 使用触摸输入：InputEventScreenTouch、InputEventScreenDrag
6. 屏幕尺寸：720x1280 竖屏

🚫 禁止使用外部资源文件（png、wav、ttf 等）
✅ 使用代码绘制：draw_rect()、draw_circle()、draw_string()
"""

                    task_description = f"""任务：{task.title}

描述：{task.description or '无详细描述'}

原始需求上下文：{plan.original_request}
{previous_tasks_context}{fix_context}{web_app_instructions}{godot_instructions}

请完成你的任务部分，提供详细的输出。"""

                    # Execute task with timeout
                    agent.update_status(AgentStatus.WORKING)
                    full_response = ""

                    try:
                        try:
                            async def execute_with_timeout():
                                nonlocal full_response
                                async for update in agent.execute_task(
                                    task_description,
                                    existing_code=existing_code,
                                    incremental_mode=incremental_mode
                                ):
                                    if update["type"] == "stream":
                                        full_response += update["content"]
                                        await self.broadcast({
                                            "type": "stream",
                                            "data": {
                                                "plan_id": plan_id,
                                                "task_id": task.id,
                                                "agent_id": agent.id,
                                                "content": update["content"],
                                            }
                                        })

                            await asyncio.wait_for(execute_with_timeout(), timeout=task_timeout)

                            # Task completed successfully
                            task_success = True

                        except asyncio.TimeoutError:
                            # Task timed out
                            task_retry_count += 1
                            error_msg = f"⚠️ 任务超时（{task_timeout}秒/15分钟），第 {task_retry_count} 次尝试失败"
                            print(f"[Pipeline] Task timeout: {task.title}, retry {task_retry_count}/{max_task_retries}")

                            await self.add_discussion_message(
                                plan_id=plan_id,
                                agent_id=agent.id,
                                agent_name=agent.name,
                                agent_type=agent.type.value,
                                content=error_msg,
                                message_type="comment",
                            )

                            if task_retry_count >= max_task_retries:
                                # All retries exhausted, restart entire pipeline
                                error_msg = f"❌ 任务「{task.title}」已重试 {max_task_retries} 次均失败，将重启整个流程"
                                print(f"[Pipeline] Task failed after {max_task_retries} retries, restarting pipeline")

                                await self.add_discussion_message(
                                    plan_id=plan_id,
                                    agent_id="system",
                                    agent_name="系统",
                                    agent_type="assistant",
                                    content=error_msg,
                                    message_type="comment",
                                )

                                # Reset all tasks to pending
                                for t in plan.tasks:
                                    t.status = TaskStatus.PENDING

                                await self.add_discussion_message(
                                    plan_id=plan_id,
                                    agent_id="system",
                                    agent_name="系统",
                                    agent_type="assistant",
                                    content="🔄 正在重新启动整个流程...",
                                    message_type="comment",
                                )

                                return await self.run_pipeline_with_plan(plan_id)

                            continue  # Retry the same task

                        except Exception as e:
                            # Task failed with error
                            error_msg = f"❌ 任务执行出错：{str(e)}"
                            print(f"[Pipeline] Task error: {task.title} - {e}")

                            await self.add_discussion_message(
                                plan_id=plan_id,
                                agent_id=agent.id,
                                agent_name=agent.name,
                                agent_type=agent.type.value,
                                content=error_msg,
                                message_type="comment",
                            )

                            task.status = TaskStatus.FAILED
                            break  # Exit retry loop on non-timeout errors
                    finally:
                        # 确保 agent 不会一直处于 WORKING（超时/异常/正常结束都恢复）
                        agent.update_status(AgentStatus.IDLE)
                        if task.status == TaskStatus.RUNNING:
                            task.status = TaskStatus.PENDING
                            self._save_plans()

                # If task was not successful after all retries, skip to next task
                if not task_success:
                    continue

                # Only process if we got a response
                if not full_response:
                    full_response = "[任务未产生输出]"

                task.status = TaskStatus.COMPLETED
                results.append({
                    "task": task.title,
                    "agent": agent.name,
                    "result": full_response,
                })
                self._save_plans()  # Persist task completion

                # Save output to files
                try:
                    if plan.target_output == "godot-game" and task.assigned_agent_type == "coder":
                        # Use Godot-specific saving for coder tasks
                        saved_files = output_manager.save_godot_project(
                            plan_id=plan_id,
                            task_title=task.title,
                            content=full_response,
                        )
                    elif plan.target_output == "web-app" and task.assigned_agent_type == "coder":
                        # For web-app coder tasks, update index.html directly
                        saved_files = output_manager.update_index_html(
                            plan_id=plan_id,
                            content=full_response,
                            task_title=task.title,
                        )
                        # Mark first coding task as completed
                        if not first_coding_task_completed:
                            first_coding_task_completed = True
                            print(f"[Coordinator] First coding task completed, incremental mode enabled for subsequent tasks")
                    else:
                        # Default saving for other output types
                        saved_files = output_manager.save_task_output(
                            plan_id=plan_id,
                            task_id=task.id,
                            task_title=task.title,
                            agent_type=task.assigned_agent_type or agent.type.value,
                            content=full_response,
                        )
                    if saved_files:
                        print(f"[OutputManager] Saved {len(saved_files)} files for task: {task.title}")
                except Exception as e:
                    print(f"[OutputManager] Error saving output: {e}")

                agent.update_status(AgentStatus.IDLE)

                # Post task completion to group chat
                summary = full_response[:200] + "..." if len(full_response) > 200 else full_response
                await self.add_discussion_message(
                    plan_id=plan_id,
                    agent_id=agent.id,
                    agent_name=agent.name,
                    agent_type=agent.type.value,
                    content=f"✅ 完成任务：{task.title}\n\n{summary}",
                    message_type="comment",
                )

                await self.broadcast({
                    "type": "plan_update",
                    "data": {
                        "plan_id": plan_id,
                        "task_id": task.id,
                        "status": "completed",
                        "result": full_response,
                    }
                })

            # Save combined output for testing
            try:
                output_manager.save_plan_output(
                    plan_id=plan_id,
                    plan_title=plan.title,
                    tasks=[t.model_dump() for t in plan.tasks],
                )
                # Consolidate web app code fragments
                if plan.target_output == "web-app":
                    output_manager.consolidate_web_app(plan_id, plan.title)
                    print(f"[OutputManager] Consolidated web app for plan {plan_id[:8]}")
                # Consolidate Godot project
                if plan.target_output == "godot-game":
                    output_manager.consolidate_godot_project(plan_id, plan.title)
                    print(f"[OutputManager] Consolidated Godot project for plan {plan_id[:8]}")
            except Exception as e:
                print(f"[OutputManager] Error saving plan output: {e}")

            # ===== Quality Scoring Gate =====
            if plan.target_output == "web-app":
                try:
                    print(f"[Coordinator] Running quality scoring...")
                    existing_code = output_manager.read_existing_code(plan_id)
                    if existing_code:
                        quality_result = quality_scorer.score_output(existing_code, plan.original_request)
                        print(f"[QualityScorer] Score: {quality_result['total']:.1f}/100 (Grade: {quality_result['grade']})")

                        # Store quality score in plan for reference
                        if not hasattr(plan, 'quality_scores'):
                            plan.quality_scores = []
                        plan.quality_scores.append({
                            "round": fix_iteration,
                            "score": quality_result["total"],
                            "grade": quality_result["grade"],
                            "timestamp": datetime.now().isoformat()
                        })

                        # Quality gate: if score is below threshold, add feedback for next iteration
                        if quality_result["total"] < 60:
                            quality_feedback = f"""⚠️ 代码质量评分: {quality_result['total']:.1f}/100 (等级: {quality_result['grade']})

评分详情:
- 完整性: {quality_result['scores']['completeness']['percentage']}%
- 正确性: {quality_result['scores']['correctness']['percentage']}%
- 可维护性: {quality_result['scores']['maintainability']['percentage']}%

需要改进的问题:
{chr(10).join('- ' + r for r in quality_result['recommendations'][:5])}

请修复这些问题后重新生成代码。"""

                            await self.add_discussion_message(
                                plan_id=plan_id,
                                agent_id="system",
                                agent_name="系统",
                                agent_type="assistant",
                                content=quality_feedback,
                                message_type="comment",
                            )

                            # Record errors for feedback learning
                            for check in quality_result['scores']['correctness'].get('checks', []):
                                if not check.get('passed', True):
                                    feedback_store.record_error(
                                        plan_id=plan_id,
                                        error_type=check.get('name', 'unknown'),
                                        description=check.get('name', 'Unknown error'),
                                        code_snippet=existing_code[:500],
                                        task_context=plan.original_request[:200]
                                    )

                            # If quality is very low, skip to next iteration
                            if quality_result["total"] < 40:
                                fix_iteration += 1
                                await self.add_discussion_message(
                                    plan_id=plan_id,
                                    agent_id="system",
                                    agent_name="系统",
                                    agent_type="assistant",
                                    content="🔄 代码质量过低，开始新一轮修复迭代...",
                                    message_type="comment",
                                )
                                continue
                        else:
                            # Good quality, post success message
                            await self.add_discussion_message(
                                plan_id=plan_id,
                                agent_id="system",
                                agent_name="系统",
                                agent_type="assistant",
                                content=f"✅ 代码质量评分通过: {quality_result['total']:.1f}/100 (等级: {quality_result['grade']})",
                                message_type="comment",
                            )
                except Exception as e:
                    print(f"[Coordinator] Quality scoring failed: {e}")
                    # Continue with execution even if quality scoring fails

            # Pre-test validation
            if plan.target_output == "web-app":
                try:
                    print(f"[Coordinator] Running pre-test validation...")
                    validation = output_manager.pre_test_validation(plan_id)

                    if not validation["passed"]:
                        # Post validation failure message
                        error_list = "\n".join([f"- ❌ {err}" for err in validation["errors"]])
                        await self.add_discussion_message(
                            plan_id=plan_id,
                            agent_id="system",
                            agent_name="系统",
                            agent_type="assistant",
                            content=f"⚠️ 预测试验证失败\n\n{error_list}\n\n请在测试前修复这些问题。",
                            message_type="comment",
                        )
                        print(f"[Coordinator] Pre-test validation failed, skipping tests")
                        # Skip to end without running tests
                        plan.status = PlanStatus.COMPLETED
                        self._save_plans()
                        return plan
                except Exception as e:
                    print(f"[Coordinator] Pre-test validation failed with error: {e}")
                    # Continue with execution even if validation fails

            # Pre-test validation for Godot
            if plan.target_output == "godot-game":
                try:
                    print(f"[Coordinator] Running Godot pre-test validation...")
                    validation = output_manager.pre_test_validation_godot(plan_id)

                    if not validation["passed"]:
                        error_list = "\n".join([f"- ❌ {err}" for err in validation["errors"]])
                        await self.add_discussion_message(
                            plan_id=plan_id,
                            agent_id="system",
                            agent_name="系统",
                            agent_type="assistant",
                            content=f"⚠️ Godot 项目验证失败\n\n{error_list}\n\n请在测试前修复这些问题。",
                            message_type="comment",
                        )
                        print(f"[Coordinator] Godot pre-test validation failed")
                        plan.status = PlanStatus.COMPLETED
                        self._save_plans()
                        return plan
                except Exception as e:
                    print(f"[Coordinator] Godot pre-test validation failed with error: {e}")
                    # Continue with execution even if validation fails

            # Execute testing tasks
            all_tests_passed = True
            test_feedback = []

            for task in testing_tasks:
                # Auto-assign tester agent if not assigned or agent not found
                if not task.assigned_agent_id:
                    # Find an available tester agent
                    tester_agents = [a for a in agent_manager.get_all_agents() if a.type.value == 'tester']
                    if tester_agents:
                        task.assigned_agent_id = tester_agents[0].id
                        self._save_plans()

                agent = agent_manager.get_agent(task.assigned_agent_id)
                if not agent:
                    # Try to find any tester agent as fallback
                    tester_agents = [a for a in agent_manager.get_all_agents() if a.type.value == 'tester']
                    if tester_agents:
                        agent = tester_agents[0]
                        task.assigned_agent_id = agent.id
                        self._save_plans()
                    else:
                        # No tester available, mark task as completed to avoid blocking
                        task.status = TaskStatus.COMPLETED
                        self._save_plans()
                        print(f"[Coordinator] No tester agent available, skipping test task: {task.title}")
                        continue

                # Post test start to group chat
                await self.add_discussion_message(
                    plan_id=plan_id,
                    agent_id=agent.id,
                    agent_name=agent.name,
                    agent_type=agent.type.value,
                    content=f"🧪 开始测试：{task.title}",
                    message_type="comment",
                )

                task.status = TaskStatus.RUNNING
                agent.update_status(AgentStatus.WORKING)

                # Read generated code for testing context
                output_dir = output_manager.get_output_path(plan_id)
                code_context = ""

                try:
                    # Read the consolidated index.html (this should have all code inline)
                    index_path = os.path.join(output_dir, "index.html")
                    if os.path.exists(index_path):
                        with open(index_path, 'r', encoding='utf-8') as f:
                            html_content = f.read()

                        # Check if the HTML has substantial inline code
                        has_inline_js = bool(re.search(
                            r'<script[^>]*>[\s\S]{500,}',  # At least 500 chars of JS
                            html_content
                        ))

                        if has_inline_js:
                            # Use the full HTML content (it's consolidated)
                            # Limit to reasonable size for LLM context
                            if len(html_content) > 20000:
                                # Try to include more of the JavaScript
                                # Find script content and prioritize it
                                script_match = re.search(r'<script[^>]*>([\s\S]*?)</script>', html_content)
                                if script_match:
                                    js_content = script_match.group(1)
                                    # Include HTML structure + full JS
                                    html_without_js = re.sub(r'<script[^>]*>[\s\S]*?</script>', '', html_content)
                                    code_context = f"\n\n生成的代码：\n```\n{html_without_js[:5000]}\n\n<script>\n{js_content[:12000]}\n</script>\n```\n"
                                else:
                                    code_context = f"\n\n生成的代码：\n```\n{html_content[:15000]}\n```\n"
                            else:
                                code_context = f"\n\n生成的代码：\n```\n{html_content}\n```\n"
                        else:
                            # Fallback: read separate JS files if HTML doesn't have inline code
                            code_parts = [f"<!-- index.html -->\n{html_content[:5000]}"]

                            # Patterns that indicate Node.js/test code
                            node_patterns = [
                                r'module\.exports',
                                r'require\s*\(',
                                r'import\s+.*from\s+["\']',
                                r'@testing-library',
                                r'jest\.mock',
                                r'describe\s*\(',
                                r'it\s*\(',
                                r'test\s*\(',
                                r'expect\s*\(',
                            ]

                            for filename in sorted(os.listdir(output_dir)):
                                if filename.endswith('.js'):
                                    js_path = os.path.join(output_dir, filename)
                                    with open(js_path, 'r', encoding='utf-8') as f:
                                        js_content = f.read()
                                        is_node_code = any(re.search(pattern, js_content) for pattern in node_patterns)
                                        if not is_node_code:
                                            code_parts.append(f"// {filename}\n{js_content[:8000]}")

                            for filename in sorted(os.listdir(output_dir)):
                                if filename.endswith('.css'):
                                    css_path = os.path.join(output_dir, filename)
                                    with open(css_path, 'r', encoding='utf-8') as f:
                                        css_content = f.read()
                                        code_parts.append(f"/* {filename} */\n{css_content[:3000]}")

                            combined_code = "\n\n".join(code_parts)
                            if len(combined_code) > 15000:
                                combined_code = combined_code[:15000] + "\n\n... (代码已截断)"
                            code_context = f"\n\n生成的代码：\n```\n{combined_code}\n```\n"

                except Exception as e:
                    print(f"[Test] Error reading code: {e}")

                # Detect technology stack from code
                tech_stack_info = ""
                if code_context:
                    if "Phaser" in code_context:
                        tech_stack_info = "\n\n【技术栈】此项目使用 Phaser.js 框架"
                    elif "getContext('2d')" in code_context or "canvas.getContext" in code_context:
                        tech_stack_info = "\n\n【技术栈】此项目使用纯 Canvas 实现，不需要 Phaser.js 等框架"
                    elif "THREE" in code_context or "Three.js" in code_context:
                        tech_stack_info = "\n\n【技术栈】此项目使用 Three.js 框架"

                test_prompt = f"""作为测试工程师，请对生成的代码进行实际验证。

原始需求：{plan.original_request}
{tech_stack_info}

测试任务：{task.title}
{code_context}

⚠️ 重要：首先识别代码使用的技术栈，只测试实际使用的技术，不要假设需要未使用的框架。

请执行以下测试步骤：
1. 代码完整性检查：检查必要功能代码是否存在（基于实际技术栈）
2. 逻辑验证：核心功能逻辑是否正确实现
3. 边界情况：是否处理了边界条件和错误情况

输出格式：
## 测试结果
- [PASS/FAIL] 测试项1: 描述
- [PASS/FAIL] 测试项2: 描述

## 发现的问题
（如果有问题，详细描述）

## 建议
（修复建议）"""

                full_response = ""
                async for update in agent.execute_task(test_prompt):
                    if update["type"] == "stream":
                        full_response += update["content"]

                task.status = TaskStatus.COMPLETED
                results.append({
                    "task": task.title,
                    "agent": agent.name,
                    "result": full_response,
                })
                self._save_plans()  # Persist test task completion

                # Check if tests passed
                if "[FAIL]" in full_response or "发现的问题" in full_response:
                    all_tests_passed = False
                    test_feedback.append(full_response)

                # Post test result to group chat
                result_emoji = "✅" if "[FAIL]" not in full_response else "❌"
                summary = full_response[:300] + "..." if len(full_response) > 300 else full_response
                await self.add_discussion_message(
                    plan_id=plan_id,
                    agent_id=agent.id,
                    agent_name=agent.name,
                    agent_type=agent.type.value,
                    content=f"{result_emoji} 测试完成：{task.title}\n\n{summary}",
                    message_type="comment",
                )

                agent.update_status(AgentStatus.IDLE)

            # Check if we need to fix bugs
            if all_tests_passed or fix_iteration >= max_fix_iterations - 1:
                break

            fix_iteration += 1

            # Post fix iteration message to group chat
            await self.add_discussion_message(
                plan_id=plan_id,
                agent_id="system",
                agent_name="系统",
                agent_type="assistant",
                content=f"🔄 测试发现问题，开始第 {fix_iteration} 轮修复...\n\n问题摘要：\n" + "\n".join([fb[:200] for fb in test_feedback]),
                message_type="comment",
            )

            # Reset coding tasks for re-execution
            for task in coding_tasks:
                if "核心" in task.title or "功能" in task.title or "实现" in task.title:
                    task.status = TaskStatus.PENDING

        # Final status
        plan.status = PlanStatus.COMPLETED
        plan.completed_at = datetime.utcnow()

        # 保存初始版本存档
        try:
            archive_path = output_manager.save_iteration_archive(plan_id, 0)
            if archive_path:
                print(f"[Coordinator] Initial version archived at: {archive_path}")
        except Exception as e:
            print(f"[Coordinator] Failed to archive initial version: {e}")

        self._save_plans()  # Persist completion

        # Post final result to discussion
        output_dir = output_manager.get_output_path(plan_id)
        if output_dir:
            preview_url = f"/api/pipeline/output/{plan_id}/files/index.html"
            result_emoji = "🎉" if all_tests_passed else "⚠️"
            status_text = "所有测试通过！" if all_tests_passed else f"经过 {fix_iteration + 1} 轮修复后完成"
            result_message = f"{result_emoji} 项目已完成！\n\n📊 状态: {status_text}\n\n📦 输出目录: {output_dir}\n\n🌐 预览地址: http://localhost:8000{preview_url}\n\n点击链接查看生成的网页。"
            await self.add_discussion_message(
                plan_id=plan_id,
                agent_id="system",
                agent_name="系统",
                agent_type="assistant",
                content=result_message,
                message_type="comment",
            )

            # Save discussion history to output directory
            try:
                discussion_path = os.path.join(output_dir, "discussion.json")
                discussion_data = {
                    "title": plan.title,
                    "original_request": plan.original_request,
                    "discussion": [msg.model_dump(mode='json') for msg in plan.discussion],
                    "saved_at": datetime.utcnow().isoformat()
                }
                with open(discussion_path, 'w', encoding='utf-8') as f:
                    json.dump(discussion_data, f, ensure_ascii=False, indent=2)
                print(f"[Coordinator] Saved discussion history to {discussion_path}")
            except Exception as e:
                print(f"[Coordinator] Error saving discussion: {e}")

        await self.broadcast({
            "type": "plan_update",
            "data": {
                "plan_id": plan_id,
                "status": "completed",
                "results": results,
                "output_url": f"/api/pipeline/output/{plan_id}/files/index.html" if output_dir else None,
            }
        })

        return json.dumps(results, ensure_ascii=False, indent=2)

    async def run_pipeline(
        self,
        request: str,
        target_output: str = "web-app",
    ) -> Plan:
        """Run the complete pipeline: Discussion → Planning → Execution"""
        # Create plan
        plan = await self.create_plan(request, target_output)
        return await self.run_pipeline_with_plan(plan.id)

    async def run_pipeline_with_plan(self, plan_id: str) -> Plan:
        """Run pipeline with existing plan"""
        plan = self.plans.get(plan_id)
        if not plan:
            raise ValueError(f"Plan {plan_id} not found")

        try:
            # Phase 1: Analyze request
            await self.analyze_request(plan.id)

            # Phase 2: Organize discussion
            await self.organize_discussion(plan.id)

            # Phase 3: Generate plan
            plan = await self.generate_plan(plan.id)

            # Phase 4: Execute plan
            await self.execute_plan(plan.id)

            return plan
        except Exception as e:
            print(f"[Pipeline Error] {e}")
            import traceback
            traceback.print_exc()
            raise

    def get_plan(self, plan_id: str) -> Optional[Plan]:
        return self.plans.get(plan_id)

    def get_all_plans(self) -> List[Plan]:
        return list(self.plans.values())

    def delete_plan(self, plan_id: str) -> bool:
        """Delete a plan by ID"""
        if plan_id in self.plans:
            del self.plans[plan_id]
            self._save_plans()
            return True
        return False

    async def start_iteration(self, plan_id: str, iteration_request: str) -> str:
        """对已完成的 plan 进行迭代，走完整流程：分析 -> 讨论 -> 计划 -> 执行

        流程：
        1. 创建新的迭代轮次
        2. 分析迭代需求
        3. 组织迭代讨论
        4. 生成迭代计划
        5. 执行迭代任务
        """
        plan = self.plans.get(plan_id)
        if not plan:
            raise ValueError(f"Plan {plan_id} not found")

        if plan.status != PlanStatus.COMPLETED:
            raise ValueError(f"Plan {plan_id} is not completed (status: {plan.status})")

        # 读取现有代码作为上下文
        existing_code = output_manager.read_existing_code(plan_id)
        if not existing_code:
            error_msg = "无法读取现有代码，迭代失败"
            await self.add_discussion_message(
                plan_id=plan_id,
                agent_id="system",
                agent_name="系统",
                agent_type="assistant",
                content=f"❌ {error_msg}",
                message_type="comment",
            )
            return error_msg

        # 创建新的迭代轮次
        round_number = len(plan.iterations) + 1
        iteration_round = IterationRound(
            round_number=round_number,
            iteration_request=iteration_request,
            status=PlanStatus.DRAFT,
        )
        plan.iterations.append(iteration_round)
        plan.current_iteration_round = round_number
        self._save_plans()

        # 广播迭代开始
        await self.broadcast({
            "type": "plan_update",
            "data": {
                "plan_id": plan_id,
                "status": "executing",
                "iteration_round": round_number,
            }
        })

        # 发送迭代开始消息
        await self._add_iteration_discussion_message(
            plan_id, round_number,
            agent_id="system",
            agent_name="系统",
            agent_type="assistant",
            content=f"🔄 开始迭代第 {round_number} 轮\n\n迭代需求：{iteration_request}",
            message_type="comment",
        )

        # Phase 1: 分析迭代需求
        try:
            await self._analyze_iteration_request(plan_id, iteration_round, existing_code, iteration_request)
        except Exception as e:
            print(f"[Coordinator] Error in _analyze_iteration_request: {e}")
            import traceback
            traceback.print_exc()

        # Phase 2: 组织迭代讨论
        try:
            await self._organize_iteration_discussion(plan_id, iteration_round, existing_code, iteration_request)
        except Exception as e:
            print(f"[Coordinator] Error in _organize_iteration_discussion: {e}")
            import traceback
            traceback.print_exc()

        # Phase 3: 生成迭代计划
        try:
            await self._generate_iteration_plan(plan_id, iteration_round, existing_code, iteration_request)
        except Exception as e:
            print(f"[Coordinator] Error in _generate_iteration_plan: {e}")
            import traceback
            traceback.print_exc()
            # 使用兜底任务
            if not iteration_round.tasks:
                all_agents = agent_manager.get_all_agents()
                coder = next((a for a in all_agents if a.type == AgentType.CODER), None)
                iteration_round.tasks = [
                    IterationTask(
                        id=str(uuid.uuid4()),
                        iteration_round=iteration_round.round_number,
                        title="实现迭代修改",
                        description=iteration_request,
                        assigned_agent_id=coder.id if coder else None,
                        assigned_agent_type="coder",
                        order=1,
                    )
                ]
                iteration_round.status = PlanStatus.APPROVED
                self._save_plans()

        # Phase 4: 执行迭代计划
        try:
            await self._execute_iteration_plan(plan_id, iteration_round, existing_code)
        except Exception as e:
            print(f"[Coordinator] Error in _execute_iteration_plan: {e}")
            import traceback
            traceback.print_exc()
            # 确保状态恢复为完成
            iteration_round.status = PlanStatus.COMPLETED
            plan.status = PlanStatus.COMPLETED
            self._save_plans()

        return f"迭代第 {round_number} 轮完成"

    async def _add_iteration_discussion_message(
        self,
        plan_id: str,
        round_number: int,
        agent_id: str,
        agent_name: str,
        agent_type: str,
        content: str,
        message_type: str = "comment",
    ):
        """添加迭代讨论消息"""
        plan = self.plans.get(plan_id)
        if not plan:
            return

        msg = DiscussionMessage(
            id=str(uuid.uuid4()),
            plan_id=plan_id,
            agent_id=agent_id,
            agent_name=agent_name,
            agent_type=agent_type,
            content=content,
            message_type=message_type,
        )

        # 添加到对应迭代轮次的讨论
        for iteration in plan.iterations:
            if iteration.round_number == round_number:
                iteration.discussion.append(msg)
                break

        plan.updated_at = datetime.utcnow()
        self._save_plans()

        await self.broadcast({
            "type": "iteration_discussion",
            "data": {
                "plan_id": plan_id,
                "iteration_round": round_number,
                "message": msg.model_dump(),
            }
        })

    async def _analyze_iteration_request(
        self,
        plan_id: str,
        iteration_round: IterationRound,
        existing_code: str,
        iteration_request: str
    ):
        """Phase 1: 分析迭代需求"""
        plan = self.plans.get(plan_id)
        if not plan:
            return

        # 找到 Assistant Agent
        all_agents = agent_manager.get_all_agents()
        assistant = next((a for a in all_agents if a.type == AgentType.ASSISTANT), None)
        if not assistant:
            assistant = all_agents[0] if all_agents else None

        if not assistant:
            return

        assistant.update_status(AgentStatus.WORKING)

        await self._add_iteration_discussion_message(
            plan_id, iteration_round.round_number,
            agent_id=assistant.id,
            agent_name=assistant.name,
            agent_type="assistant",
            content=f"我来分析一下迭代需求：{iteration_request}",
            message_type="comment",
        )

        # 截取代码以避免上下文过长
        code_preview = existing_code[:5000] if len(existing_code) > 5000 else existing_code

        analysis_prompt = f"""请分析以下迭代需求：

原始需求：{plan.original_request}

迭代需求：{iteration_request}

现有代码预览：
```
{code_preview}
```

请输出：
1. 迭代需求分析（2-3句话概括需要修改什么）
2. 影响范围（需要修改哪些模块）
3. 技术建议

保持简洁，不要输出代码。"""

        full_response = ""
        try:
            async for chunk in glm_client.chat_stream(analysis_prompt, "assistant"):
                full_response += chunk
                await self.broadcast({
                    "type": "stream",
                    "data": {
                        "plan_id": plan_id,
                        "iteration_round": iteration_round.round_number,
                        "agent_id": assistant.id,
                        "content": chunk,
                    }
                })
        except Exception as e:
            print(f"[Coordinator] Error in _analyze_iteration_request: {e}")
            full_response = f"分析出错: {str(e)}"

        await self._add_iteration_discussion_message(
            plan_id, iteration_round.round_number,
            agent_id=assistant.id,
            agent_name=assistant.name,
            agent_type="assistant",
            content=full_response,
            message_type="proposal",
        )

        iteration_round.status = PlanStatus.DISCUSSING
        self._save_plans()
        assistant.update_status(AgentStatus.IDLE)

    async def _organize_iteration_discussion(
        self,
        plan_id: str,
        iteration_round: IterationRound,
        existing_code: str,
        iteration_request: str
    ):
        """Phase 2: 组织迭代讨论"""
        plan = self.plans.get(plan_id)
        if not plan:
            return

        # 获取选中的 agents
        all_agents = agent_manager.get_all_agents()
        if plan.selected_agent_ids:
            selected_agents = [a for a in all_agents if a.id in plan.selected_agent_ids]
        else:
            selected_agents = all_agents

        if not selected_agents:
            return

        # 找到 assistant
        assistant = next((a for a in selected_agents if a.type == AgentType.ASSISTANT), None)
        if not assistant:
            assistant = selected_agents[0]

        # Assistant 发起讨论
        await self._add_iteration_discussion_message(
            plan_id, iteration_round.round_number,
            agent_id=assistant.id,
            agent_name=assistant.name,
            agent_type=assistant.type.value,
            content=f"各位，针对这次迭代需求「{iteration_request}」，请发表你们的看法。",
            message_type="question",
        )

        # Agent 类型的 prompt 模板
        agent_prompts = {
            AgentType.CODER: """作为代码开发专家，请针对以下迭代需求给出你的技术建议：

迭代需求：{request}

请简短说明：
1. 推荐的修改方案
2. 需要注意的风险点
3. 实现步骤建议

保持简洁，每项1-2句话。""",

            AgentType.ANALYST: """作为数据分析师，请针对以下迭代需求给出你的分析：

迭代需求：{request}

请简短说明：
1. 迭代可行性评估
2. 潜在影响
3. 建议

保持简洁，每项1-2句话。""",

            AgentType.TESTER: """作为测试工程师，请针对以下迭代需求给出你的测试建议：

迭代需求：{request}

请简短说明：
1. 需要测试的变更点
2. 测试场景建议
3. 质量保证建议

保持简洁，每项1-2句话。""",

            AgentType.ASSISTANT: """作为项目助手，请针对以下迭代需求给出你的建议：

迭代需求：{request}

请简短说明你的专业观点和建议。保持简洁。""",
        }

        # 让每个 agent（除 assistant）参与讨论
        for agent in selected_agents:
            if agent.id == assistant.id:
                continue

            agent.update_status(AgentStatus.WORKING)

            prompt_template = agent_prompts.get(agent.type)
            if not prompt_template:
                prompt_template = f"""作为{agent.name}，请针对以下迭代需求给出你的专业建议：

迭代需求：{{request}}

请简短说明你的专业观点和建议。保持简洁。"""

            prompt = prompt_template.format(request=iteration_request)

            if agent.custom_prompt:
                prompt = f"{agent.custom_prompt}\n\n{prompt}"

            response = ""
            try:
                async def _collect_response():
                    nonlocal response
                    async for chunk in glm_client.chat_stream(prompt, agent.type.value):
                        response += chunk
                await asyncio.wait_for(_collect_response(), timeout=60)
            except asyncio.TimeoutError:
                response = f"(该 Agent 回复超时，已跳过)"
            except Exception as e:
                response = f"(回复出错: {str(e)[:100]})"

            await self._add_iteration_discussion_message(
                plan_id, iteration_round.round_number,
                agent_id=agent.id,
                agent_name=agent.name,
                agent_type=agent.type.value,
                content=response,
                message_type="proposal",
            )
            agent.update_status(AgentStatus.IDLE)

        # Assistant 总结
        await self._add_iteration_discussion_message(
            plan_id, iteration_round.round_number,
            agent_id=assistant.id,
            agent_name=assistant.name,
            agent_type=assistant.type.value,
            content="感谢各位的建议。我来总结一下，形成迭代计划。",
            message_type="comment",
        )

    async def _generate_iteration_plan(
        self,
        plan_id: str,
        iteration_round: IterationRound,
        existing_code: str,
        iteration_request: str
    ):
        """Phase 3: 生成迭代计划"""
        plan = self.plans.get(plan_id)
        if not plan:
            return

        # 获取选中的 agents
        all_agents = agent_manager.get_all_agents()
        if plan.selected_agent_ids:
            selected_agents = [a for a in all_agents if a.id in plan.selected_agent_ids]
        else:
            selected_agents = all_agents

        # 找到 assistant
        assistant = next((a for a in selected_agents if a.type == AgentType.ASSISTANT), None)
        if not assistant and selected_agents:
            assistant = selected_agents[0]

        if not assistant:
            return

        # 构建 agent 类型映射，尊重用户选择顺序
        agents_by_type = {}
        if plan.selected_agent_ids:
            for agent_id in plan.selected_agent_ids:
                agent = next((a for a in selected_agents if a.id == agent_id), None)
                if agent:
                    agent_type = agent.type.value if hasattr(agent.type, 'value') else str(agent.type)
                    if agent_type not in agents_by_type:
                        agents_by_type[agent_type] = agent
        else:
            for agent in selected_agents:
                agent_type = agent.type.value if hasattr(agent.type, 'value') else str(agent.type)
                if agent_type not in agents_by_type:
                    agents_by_type[agent_type] = agent

        assistant.update_status(AgentStatus.WORKING)

        # 编译讨论摘要
        discussion_summary = "\n".join([
            f"[{msg.agent_name}]: {msg.content}"
            for msg in iteration_round.discussion[-5:]
        ])

        available_agent_types = list(agents_by_type.keys())
        agent_types_str = "/".join(available_agent_types)

        # 截取代码
        code_preview = existing_code[:3000] if len(existing_code) > 3000 else existing_code

        plan_prompt = f"""基于以下信息，请生成迭代执行计划：

原始需求：{plan.original_request}
迭代需求：{iteration_request}

现有代码预览：
```
{code_preview}
```

讨论摘要：
{discussion_summary}

可用的Agent类型：{agent_types_str}

⚠️ 迭代任务要求：
1. 任务数量控制在3-5个以内，聚焦于迭代需求
2. 每个任务应该是一个具体的修改点
3. 优先分配给 coder 类型 agent

请以JSON格式输出执行计划：
{{
  "tasks": [
    {{
      "title": "任务标题",
      "description": "任务描述",
      "assigned_agent_type": "coder",
      "order": 1
    }}
  ]
}}"""

        full_response = ""
        try:
            async def _stream_plan_response():
                nonlocal full_response
                async for chunk in glm_client.chat_stream(plan_prompt, "assistant"):
                    full_response += chunk
                return full_response

            full_response = await asyncio.wait_for(_stream_plan_response(), timeout=60)
        except asyncio.TimeoutError:
            full_response = ""
        except Exception as e:
            full_response = ""

        # 解析 JSON
        try:
            if full_response and "{" in full_response and "}" in full_response:
                json_start = full_response.find("{")
                json_end = full_response.rfind("}") + 1
                json_str = full_response[json_start:json_end]
                plan_data = json.loads(json_str)

                # 排除无法自动执行的任务关键词
                # 1. 用户测试类：需要用户主动操作
                # 2. 外部资源类：需要外部图片、音频、视频等资源文件
                # 3. 验证类：需要人工验证功能
                excluded_task_keywords = [
                    # 用户测试类
                    "用户测试", "用户反馈", "反馈调整", "测试与反馈", "收集反馈",
                    # 外部资源类
                    "更新资源文件", "资源文件", "图片资源", "音频文件", "视频文件",
                    "素材替换", "图片替换", "添加图片", "添加素材", "上传资源",
                    # 验证类
                    "验证", "检查功能", "确认功能", "测试功能",
                    # 3D建模/动画类
                    "3D建模", "建模", "材质制作", "动画制作", "模型制作", "贴图制作"
                ]

                task_order = 0
                for task_data in plan_data.get("tasks", []):
                    title = task_data.get("title", "")
                    description = task_data.get("description", "")

                    # 跳过无法自动执行的任务
                    task_text = f"{title} {description}"
                    if any(keyword in task_text for keyword in excluded_task_keywords):
                        print(f"[Coordinator] Skipping non-automatable task: {title}")
                        continue

                    agent_type_str = task_data.get("assigned_agent_type", "coder")
                    assigned_agent = agents_by_type.get(agent_type_str)
                    assigned_agent_id = assigned_agent.id if assigned_agent else None

                    task_order += 1
                    iteration_round.tasks.append(IterationTask(
                        id=str(uuid.uuid4()),
                        iteration_round=iteration_round.round_number,
                        title=title or "未命名任务",
                        description=description,
                        assigned_agent_id=assigned_agent_id,
                        assigned_agent_type=agent_type_str,
                        order=task_order,
                    ))

            # 如果没有解析到任务，使用兜底任务
            if not iteration_round.tasks:
                raise ValueError("No tasks parsed from response")

        except Exception as e:
            print(f"[Coordinator] _generate_iteration_plan parse error: {e}, using fallback")
            # 使用兜底任务 - 确保总是有任务
            fallback_agent = agents_by_type.get("coder") or agents_by_type.get("assistant") or (selected_agents[0] if selected_agents else None)

            # 如果还是没有 agent，从所有 agent 中找一个
            if not fallback_agent:
                all_agents_list = agent_manager.get_all_agents()
                fallback_agent = next((a for a in all_agents_list if a.type == AgentType.CODER), None)
                if not fallback_agent:
                    fallback_agent = all_agents_list[0] if all_agents_list else None

            iteration_round.tasks = [
                IterationTask(
                    id=str(uuid.uuid4()),
                    iteration_round=iteration_round.round_number,
                    title="实现迭代修改",
                    description=iteration_request,
                    assigned_agent_id=fallback_agent.id if fallback_agent else None,
                    assigned_agent_type=fallback_agent.type.value if fallback_agent else "coder",
                    order=1,
                )
            ]
            print(f"[Coordinator] Created fallback task with agent: {fallback_agent.name if fallback_agent else 'None'}")

        iteration_round.status = PlanStatus.PENDING_APPROVAL
        self._save_plans()

        await self.broadcast({
            "type": "iteration_pending_approval",
            "data": {
                "plan_id": plan_id,
                "iteration_round": iteration_round.round_number,
                "plan": plan.model_dump(),
                "message": "迭代计划已生成，请确认后开始执行"
            }
        })

        assistant.update_status(AgentStatus.IDLE)

    async def _execute_iteration_plan(
        self,
        plan_id: str,
        iteration_round: IterationRound,
        existing_code: str
    ):
        """Phase 4: 执行迭代计划"""
        plan = self.plans.get(plan_id)
        if not plan:
            return

        iteration_round.status = PlanStatus.EXECUTING
        self._save_plans()

        await self._add_iteration_discussion_message(
            plan_id, iteration_round.round_number,
            agent_id="system",
            agent_name="系统",
            agent_type="assistant",
            content=f"🚀 开始执行迭代计划，共 {len(iteration_round.tasks)} 个任务。",
            message_type="comment",
        )

        await self.broadcast({
            "type": "plan_update",
            "data": {
                "plan_id": plan_id,
                "status": "executing",
                "iteration_round": iteration_round.round_number,
            }
        })

        # 按顺序执行任务
        sorted_tasks = sorted(iteration_round.tasks, key=lambda t: t.order)
        current_code = existing_code

        for task in sorted_tasks:
            # 检查是否请求停止迭代
            if self.should_stop_iteration(plan_id, iteration_round.round_number):
                print(f"[Coordinator] Iteration {iteration_round.round_number} stopped by user request")
                iteration_round.status = PlanStatus.COMPLETED
                iteration_round.completed_at = datetime.utcnow()
                self._save_plans()
                await self._add_iteration_discussion_message(
                    plan_id, iteration_round.round_number,
                    agent_id="system",
                    agent_name="系统",
                    agent_type="assistant",
                    content=f"⏹️ 迭代已被用户停止",
                    message_type="comment",
                )
                await self.broadcast({
                    "type": "plan_update",
                    "data": {
                        "plan_id": plan_id,
                        "plan": plan.model_dump(),
                        "status": "completed",
                        "iteration_round": iteration_round.round_number,
                        "stopped": True,
                    }
                })
                self.clear_stop_flag(plan_id, iteration_round.round_number)
                return

            if not task.assigned_agent_id:
                continue

            agent = agent_manager.get_agent(task.assigned_agent_id)
            if not agent:
                continue

            agent.update_status(AgentStatus.WORKING)
            task.status = TaskStatus.RUNNING

            await self._add_iteration_discussion_message(
                plan_id, iteration_round.round_number,
                agent_id=agent.id,
                agent_name=agent.name,
                agent_type=agent.type.value,
                content=f"📝 开始任务：{task.title}",
                message_type="comment",
            )

            await self.broadcast({
                "type": "iteration_task_update",
                "data": {
                    "plan_id": plan_id,
                    "iteration_round": iteration_round.round_number,
                    "task_id": task.id,
                    "status": "running",
                }
            })

            # 截断代码以节省 token（只显示前后部分）
            code_preview = current_code
            if len(current_code) > 8000:
                # 显示前 4000 和后 3000 字符
                code_preview = current_code[:4000] + "\n\n... [代码已截断，中间部分省略] ...\n\n" + current_code[-3000:]

            # 构建迭代任务描述 - 使用增量修改格式
            iteration_prompt = f"""你是专业的开发工程师。现在需要对现有代码进行**增量修改**。

## 原始需求
{plan.original_request}

## 迭代需求
{iteration_round.iteration_request}

## 当前任务
{task.title}
{task.description or ''}

## 现有代码（仅供参考，理解结构即可）
```
{code_preview}
```

## 🎯 输出格式要求（必须严格遵守）

### 第一步：分析（必须）
简要说明：
- 你要修改哪些函数/CSS规则
- 修改的目的
- 修改后如何满足迭代需求

### 第二步：输出修改块
只输出需要修改的部分，使用以下格式：

**修改现有函数：**
<<<MODIFY: 函数名>>>
function 函数名(参数) {{
    // 完整的新函数代码
}}
<<<END>>>

**在某个函数后新增代码：**
<<<ADD: after:现有函数名>>>
// 新增的代码
<<<END>>>

**在某个函数前新增代码：**
<<<ADD: before:现有函数名>>>
// 新增的代码
<<<END>>>

**删除函数：**
<<<DELETE: 函数名>>>
<<<END>>>

**修改 CSS 规则：**
<<<CSS: .selector>>>
    property: value;
    another-property: value;
<<<END>>>

### ⚠️ 重要规则
1. **只输出需要修改的块**，不要输出未改动的代码
2. 每个修改块必须**完整**（函数体不能省略）
3. **未列出的函数/CSS规则保持不变**
4. 如果需要大范围重构（超过5个函数），可以输出完整 HTML（用 ```html 包裹）
5. 所有 CSS 和 JS 必须内联
6. 代码必须可以直接在浏览器中运行

### 常见错误提醒
- 如果迭代需求是"当X发生时执行Y"，确保代码中同时包含X的检测和Y的执行
- 如果迭代需求涉及UI更新，确保DOM元素正确引用
- 如果迭代需求涉及状态变化，确保状态变量和显示都更新

请先分析，然后输出修改块。"""

            full_response = ""
            task_timeout = 600  # 10 分钟超时

            try:
                async def execute_with_timeout():
                    nonlocal full_response
                    # 使用 glm_coding_client (GLM-5 + Coding Plan) 进行代码生成
                    async for chunk in glm_coding_client.chat_stream(iteration_prompt, agent.type.value):
                        full_response += chunk
                        await self.broadcast({
                            "type": "stream",
                            "data": {
                                "plan_id": plan_id,
                                "iteration_round": iteration_round.round_number,
                                "task_id": task.id,
                                "agent_id": agent.id,
                                "content": chunk,
                            }
                        })

                await asyncio.wait_for(execute_with_timeout(), timeout=task_timeout)

            except asyncio.TimeoutError:
                full_response = f"任务超时（{task_timeout}秒）"
            except Exception as e:
                full_response = f"任务执行出错：{str(e)}"
            finally:
                agent.update_status(AgentStatus.IDLE)

            # 检查是否有有效代码或修改块
            if full_response and "错误" not in full_response[:100]:
                code_updated = False

                # 优先检查是否使用了增量修改格式
                if code_merger.has_modifications(full_response):
                    # 使用增量合并模式
                    modifications = code_merger.parse_modifications(full_response)
                    if modifications:
                        merge_result = code_merger.merge_html(current_code, modifications)
                        current_code = merge_result.code
                        code_updated = merge_result.applied > 0

                        print(f"[Iteration] Applied {merge_result.applied}/{len(modifications)} modifications")
                        if merge_result.failed:
                            print(f"[Iteration] Failed modifications: {merge_result.failed}")

                        # 记录修改内容
                        mod_summary = ", ".join([f"{m.type}:{m.target}" for m in modifications])
                        status_emoji = "✅" if not merge_result.failed else "⚠️"
                        await self._add_iteration_discussion_message(
                            plan_id, iteration_round.round_number,
                            agent_id=agent.id,
                            agent_name=agent.name,
                            agent_type=agent.type.value,
                            content=f"{status_emoji} 增量修改 ({merge_result.applied}个)：{mod_summary}",
                            message_type="comment",
                        )

                # 如果没有修改块，检查是否输出完整 HTML（兼容模式）
                if not code_updated and '<html' in full_response.lower():
                    # 先尝试从 markdown 代码块中提取
                    code_block_match = re.search(
                        r'```(?:html)?\s*\n(.*?)```',
                        full_response,
                        re.IGNORECASE | re.DOTALL
                    )
                    extract_from = code_block_match.group(1) if code_block_match else full_response

                    # 提取 HTML 代码
                    html_match = re.search(
                        r'(<(!DOCTYPE\s+)?html.*?</html>)',
                        extract_from,
                        re.IGNORECASE | re.DOTALL
                    )
                    if html_match:
                        current_code = html_match.group(1)
                        code_updated = True
                        print(f"[Iteration] Using full HTML replacement (fallback mode)")
                    elif code_block_match:
                        # 如果代码块中没有完整的html标签，使用代码块内容
                        current_code = code_block_match.group(1).strip()
                        code_updated = True

                # 验证并保存代码
                if code_updated:
                    # 检查是否是 HTML 内容
                    is_html_content = current_code.strip().lower().startswith('<!doctype') or \
                                   current_code.strip().lower().startswith('<html')

                    if is_html_content:
                        # 验证 HTML 结构完整性
                        is_complete, error_msg = self._validate_html_completeness(current_code)
                        if is_complete:
                            task.status = TaskStatus.COMPLETED

                            # 保存到输出目录
                            try:
                                plan_dir = output_manager.get_output_path(plan_id)
                                index_path = os.path.join(plan_dir, "index.html")
                                with open(index_path, 'w', encoding='utf-8') as f:
                                    f.write(current_code)
                            except Exception as e:
                                print(f"[Coordinator] Error saving iteration code: {e}")

                            await self._add_iteration_discussion_message(
                                plan_id, iteration_round.round_number,
                                agent_id=agent.id,
                                agent_name=agent.name,
                                agent_type=agent.type.value,
                                content=f"✅ 完成任务：{task.title}",
                                message_type="comment",
                            )
                        else:
                            # HTML 不完整，标记失败并请求重试
                            task.status = TaskStatus.FAILED
                            print(f"[Coordinator] HTML validation failed: {error_msg}")
                            await self._add_iteration_discussion_message(
                                plan_id, iteration_round.round_number,
                                agent_id=agent.id,
                                agent_name=agent.name,
                                agent_type=agent.type.value,
                                content=f"❌ HTML 生成不完整：{error_msg}\n\n请重新生成完整的 HTML 代码，确保包含所有必要的闭合标签（</head>, </body>, </html> 等）。",
                                message_type="comment",
                            )
                    else:
                        # 测试报告等非代码输出，标记完成但不更新代码
                        task.status = TaskStatus.COMPLETED
                        print(f"[Coordinator] Task output is not valid HTML, skipping index.html update")

                        await self._add_iteration_discussion_message(
                            plan_id, iteration_round.round_number,
                            agent_id=agent.id,
                            agent_name=agent.name,
                            agent_type=agent.type.value,
                            content=f"✅ 完成任务：{task.title}",
                            message_type="comment",
                        )
                else:
                    # 没有检测到有效代码，但可能是纯文本回复（如分析说明）
                    if full_response.strip():
                        task.status = TaskStatus.COMPLETED
                        print(f"[Coordinator] Task completed without code changes")
                    else:
                        task.status = TaskStatus.FAILED
            else:
                task.status = TaskStatus.FAILED
                await self._add_iteration_discussion_message(
                    plan_id, iteration_round.round_number,
                    agent_id=agent.id,
                    agent_name=agent.name,
                    agent_type=agent.type.value,
                    content=f"❌ 任务失败：{task.title}\n\n{full_response[:200]}",
                    message_type="comment",
                )

            self._save_plans()

            await self.broadcast({
                "type": "iteration_task_update",
                "data": {
                    "plan_id": plan_id,
                    "iteration_round": iteration_round.round_number,
                    "task_id": task.id,
                    "status": task.status.value,
                }
            })

        # 迭代完成
        iteration_round.status = PlanStatus.COMPLETED
        iteration_round.completed_at = datetime.utcnow()

        # 保存迭代存档
        try:
            archive_path = output_manager.save_iteration_archive(plan_id, iteration_round.round_number)
            if archive_path:
                iteration_round.archive_path = archive_path
                print(f"[Coordinator] Iteration {iteration_round.round_number} archived at: {archive_path}")
        except Exception as e:
            print(f"[Coordinator] Failed to archive iteration: {e}")

        plan.status = PlanStatus.COMPLETED
        plan.updated_at = datetime.utcnow()
        self._save_plans()

        preview_url = f"/api/pipeline/output/{plan_id}/files/index.html"
        await self._add_iteration_discussion_message(
            plan_id, iteration_round.round_number,
            agent_id="system",
            agent_name="系统",
            agent_type="assistant",
            content=f"🎉 迭代第 {iteration_round.round_number} 轮完成！\n\n🌐 预览地址: http://localhost:8000{preview_url}",
            message_type="comment",
        )

        await self.broadcast({
            "type": "plan_update",
            "data": {
                "plan_id": plan_id,
                "plan": plan.model_dump(),  # 发送完整 plan 数据以更新迭代状态
                "status": "completed",
                "iteration_round": iteration_round.round_number,
                "output_url": preview_url,
                "archive_created": True,  # 通知前端存档已创建
            }
        })

    def _validate_html_completeness(self, html: str) -> tuple:
        """验证 HTML 结构完整性

        Returns:
            (is_valid, error_message)
        """
        html_lower = html.lower().strip()

        # 检查必要的开始标签
        if not (html_lower.startswith('<!doctype') or html_lower.startswith('<html')):
            return False, "缺少 DOCTYPE 或 <html> 开始标签"

        # 检查必要的结束标签
        required_end_tags = ['</html>', '</body>', '</head>']
        for tag in required_end_tags:
            if tag not in html_lower:
                return False, f"缺少 {tag} 标签"

        # 检查 <style> 标签配对
        style_opens = html_lower.count('<style')
        style_closes = html_lower.count('</style>')
        if style_opens != style_closes:
            return False, f"<style> 标签不配对: {style_opens} 个开始, {style_closes} 个结束"

        # 检查 <script> 标签配对
        script_opens = html_lower.count('<script')
        script_closes = html_lower.count('</script>')
        if script_opens != script_closes:
            return False, f"<script> 标签不配对: {script_opens} 个开始, {script_closes} 个结束"

        return True, ""

    # 保留旧方法作为兼容
    async def iterate_plan(self, plan_id: str, iteration_request: str) -> str:
        """对已完成的 plan 进行迭代（兼容旧接口）"""
        return await self.start_iteration(plan_id, iteration_request)


# Global instance
coordinator = CoordinatorService()
