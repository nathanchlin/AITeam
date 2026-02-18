import asyncio
import os
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid
import json
from pathlib import Path
from app.services.agent_manager import agent_manager
from app.services.output_manager import output_manager
from app.models.schemas import (
    AgentType, AgentStatus, TaskStatus, PlanStatus,
    Plan, PlanTask, PlanCreate, DiscussionMessage
)
from app.llm.glm_client import glm_client

# Storage path for plan persistence
PLANS_STORAGE_FILE = Path(__file__).parent.parent.parent / "data" / "plans.json"


class CoordinatorService:
    def __init__(self):
        self.plans: Dict[str, Plan] = {}
        self.websocket_manager = None
        # Load persisted plans on initialization
        self._load_plans()

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

        # Get current agents by type
        agents_by_type = {}
        for agent in agent_manager.get_all_agents():
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

    async def broadcast(self, message: Dict[str, Any]):
        if self.websocket_manager:
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
            async for chunk in glm_client.chat_stream(prompt, agent.type.value):
                response += chunk

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
        agents_by_type = {}
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

        plan_prompt = f"""基于以下讨论，请生成详细的执行计划：

原始需求：{plan.original_request}
目标输出：{plan.target_output}

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
        async for chunk in glm_client.chat_stream(plan_prompt, "assistant"):
            full_response += chunk

        # Parse JSON from response
        try:
            # Extract JSON from response
            json_start = full_response.find("{")
            json_end = full_response.rfind("}") + 1
            json_str = full_response[json_start:json_end]
            plan_data = json.loads(json_str)

            plan.title = plan_data.get("title", plan.title)
            plan.description = plan_data.get("description", "")

            # Create plan tasks
            for i, task_data in enumerate(plan_data.get("tasks", [])):
                agent_type_str = task_data.get("assigned_agent_type", "coder")
                assigned_agent_id = None

                # Find the right agent from selected agents
                if agent_type_str in agents_by_type:
                    assigned_agent_id = agents_by_type[agent_type_str].id

                plan_task = PlanTask(
                    id=str(uuid.uuid4()),
                    title=task_data.get("title", "未命名任务"),
                    description=task_data.get("description", ""),
                    assigned_agent_id=assigned_agent_id,
                    assigned_agent_type=agent_type_str,
                    order=i + 1,
                )
                plan.tasks.append(plan_task)

        except json.JSONDecodeError as e:
            # Fallback: create a simple plan
            plan.description = full_response
            # Assign to first available coder or assistant
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

        plan.status = PlanStatus.APPROVED
        plan.updated_at = datetime.utcnow()
        self._save_plans()  # Persist after generating plan

        # Add plan to broadcast
        await self.broadcast({
            "type": "plan_update",
            "data": {
                "plan_id": plan_id,
                "plan": plan.model_dump(),
            }
        })

        assistant.update_status(AgentStatus.IDLE)
        return plan

    async def execute_plan(self, plan_id: str) -> str:
        """Phase 4: Execute the plan step by step with testing and feedback loop"""
        plan = self.plans.get(plan_id)
        if not plan:
            return "Plan not found"

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

                    # Add web-app specific instructions
                    web_app_instructions = ""
                    if plan.target_output == "web-app" and agent.type.value == "coder":
                        web_app_instructions = """

⚠️ Web应用开发要求：
1. 生成完整的单文件 HTML（包含内联 CSS 和 JavaScript）
2. 不要引用外部文件（如 js/xxx.js, css/xxx.css）
3. 所有代码必须完整可运行，不能只写片段或伪代码
4. 必须包含初始化代码（window.onload 或 DOMContentLoaded）
5. 对于游戏，必须包含：游戏循环、初始化函数、事件绑定"""

                    task_description = f"""任务：{task.title}

描述：{task.description or '无详细描述'}

原始需求上下文：{plan.original_request}
{fix_context}{web_app_instructions}

请完成你的任务部分，提供详细的输出。"""

                    # Execute task with timeout
                    agent.update_status(AgentStatus.WORKING)
                    full_response = ""

                    try:
                        async def execute_with_timeout():
                            nonlocal full_response
                            async for update in agent.execute_task(task_description):
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

                        agent.update_status(AgentStatus.IDLE)

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

                            # Restart pipeline from beginning
                            await self.add_discussion_message(
                                plan_id=plan_id,
                                agent_id="system",
                                agent_name="系统",
                                agent_type="assistant",
                                content="🔄 正在重新启动整个流程...",
                                message_type="comment",
                            )

                            # Recursively restart pipeline
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
                        agent.update_status(AgentStatus.IDLE)
                        break  # Exit retry loop on non-timeout errors

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
            except Exception as e:
                print(f"[OutputManager] Error saving plan output: {e}")

            # Execute testing tasks
            all_tests_passed = True
            test_feedback = []

            for task in testing_tasks:
                if not task.assigned_agent_id:
                    continue

                agent = agent_manager.get_agent(task.assigned_agent_id)
                if not agent:
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

                # Patterns that indicate Node.js/test code (not browser-compatible)
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

                try:
                    # Read all relevant code files
                    code_parts = []

                    # Read index.html
                    index_path = os.path.join(output_dir, "index.html")
                    if os.path.exists(index_path):
                        with open(index_path, 'r', encoding='utf-8') as f:
                            html_content = f.read()
                            code_parts.append(f"<!-- index.html -->\n{html_content[:5000]}")

                    # Read JavaScript files (skip Node.js/test code)
                    for filename in sorted(os.listdir(output_dir)):
                        if filename.endswith('.js'):
                            js_path = os.path.join(output_dir, filename)
                            with open(js_path, 'r', encoding='utf-8') as f:
                                js_content = f.read()

                                # Skip Node.js/test code
                                is_node_code = any(re.search(pattern, js_content) for pattern in node_patterns)
                                if not is_node_code:
                                    code_parts.append(f"// {filename}\n{js_content[:8000]}")

                    # Read CSS files
                    for filename in sorted(os.listdir(output_dir)):
                        if filename.endswith('.css'):
                            css_path = os.path.join(output_dir, filename)
                            with open(css_path, 'r', encoding='utf-8') as f:
                                css_content = f.read()
                                code_parts.append(f"/* {filename} */\n{css_content[:3000]}")

                    if code_parts:
                        combined_code = "\n\n".join(code_parts)
                        # Limit total size to avoid token limits
                        if len(combined_code) > 15000:
                            combined_code = combined_code[:15000] + "\n\n... (代码已截断)"
                        code_context = f"\n\n生成的代码：\n```\n{combined_code}\n```\n"
                except Exception as e:
                    print(f"[Test] Error reading code: {e}")

                test_prompt = f"""作为测试工程师，请对生成的代码进行实际验证。

原始需求：{plan.original_request}

测试任务：{task.title}
{code_context}

请执行以下测试步骤：
1. 代码完整性检查：是否包含所有必要的功能代码
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
                    "discussion": [msg.model_dump() for msg in plan.discussion],
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


# Global instance
coordinator = CoordinatorService()
