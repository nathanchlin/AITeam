import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid
import json
from app.services.agent_manager import agent_manager
from app.models.schemas import (
    AgentType, AgentStatus, TaskStatus, PlanStatus,
    Plan, PlanTask, PlanCreate, DiscussionMessage
)
from app.llm.glm_client import glm_client


class CoordinatorService:
    def __init__(self):
        self.plans: Dict[str, Plan] = {}
        self.websocket_manager = None

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
    ) -> Plan:
        """Create a new plan from a user request"""
        plan_id = str(uuid.uuid4())
        plan = Plan(
            id=plan_id,
            title=f"计划: {request[:50]}...",
            original_request=request,
            target_output=target_output,
            created_by_agent_id=created_by_agent_id,
            status=PlanStatus.DRAFT,
        )
        self.plans[plan_id] = plan
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

        # Get all agents
        agents = agent_manager.get_all_agents()

        # Assistant initiates discussion
        assistant = next((a for a in agents if a.type == AgentType.ASSISTANT), None)
        coder = next((a for a in agents if a.type == AgentType.CODER), None)
        analyst = next((a for a in agents if a.type == AgentType.ANALYST), None)
        tester = next((a for a in agents if a.type == AgentType.TESTER), None)

        if not all([assistant, coder, analyst, tester]):
            return "Not all required agents found"

        # Assistant asks for opinions
        await self.add_discussion_message(
            plan_id, assistant.id, assistant.name, "assistant",
            "各位，请针对这个项目发表你们的看法和建议。",
            "question"
        )

        # Coder's input
        coder.update_status(AgentStatus.WORKING)
        coder_prompt = f"""作为代码开发专家，请针对以下项目需求给出你的技术建议：

需求：{plan.original_request}

请简短说明：
1. 推荐的技术栈
2. 需要实现的核心模块
3. 预计的开发步骤（3-5步）

保持简洁，每项1-2句话。"""

        coder_response = ""
        async for chunk in glm_client.chat_stream(coder_prompt, "coder"):
            coder_response += chunk

        await self.add_discussion_message(
            plan_id, coder.id, coder.name, "coder",
            coder_response,
            "proposal"
        )
        coder.update_status(AgentStatus.IDLE)

        # Analyst's input
        analyst.update_status(AgentStatus.WORKING)
        analyst_prompt = f"""作为数据分析师，请针对以下项目给出你的分析：

需求：{plan.original_request}

请简短说明：
1. 项目可行性评估
2. 潜在风险点
3. 性能考量

保持简洁，每项1-2句话。"""

        analyst_response = ""
        async for chunk in glm_client.chat_stream(analyst_prompt, "analyst"):
            analyst_response += chunk

        await self.add_discussion_message(
            plan_id, analyst.id, analyst.name, "analyst",
            analyst_response,
            "proposal"
        )
        analyst.update_status(AgentStatus.IDLE)

        # Tester's input
        tester.update_status(AgentStatus.WORKING)
        tester_prompt = f"""作为测试工程师，请针对以下项目给出你的测试建议：

需求：{plan.original_request}

请简短说明：
1. 需要测试的核心功能
2. 关键测试场景
3. 质量保证建议

保持简洁，每项1-2句话。"""

        tester_response = ""
        async for chunk in glm_client.chat_stream(tester_prompt, "tester"):
            tester_response += chunk

        await self.add_discussion_message(
            plan_id, tester.id, tester.name, "tester",
            tester_response,
            "proposal"
        )
        tester.update_status(AgentStatus.IDLE)

        # Assistant summarizes
        await self.add_discussion_message(
            plan_id, assistant.id, assistant.name, "assistant",
            "感谢各位的建议。我来总结一下大家的意见，形成最终计划。",
            "comment"
        )

        return "Discussion completed"

    async def generate_plan(self, plan_id: str) -> Plan:
        """Phase 3: Generate detailed execution plan"""
        plan = self.plans.get(plan_id)
        if not plan:
            raise ValueError(f"Plan {plan_id} not found")

        # Get agents
        agents = agent_manager.get_all_agents()
        assistant = next((a for a in agents if a.type == AgentType.ASSISTANT), None)
        coder = next((a for a in agents if a.type == AgentType.CODER), None)
        analyst = next((a for a in agents if a.type == AgentType.ANALYST), None)
        tester = next((a for a in agents if a.type == AgentType.TESTER), None)

        if not assistant:
            raise ValueError("No Assistant agent found")

        assistant.update_status(AgentStatus.WORKING)

        # Compile discussion summary
        discussion_summary = "\n".join([
            f"[{msg.agent_name}]: {msg.content}"
            for msg in plan.discussion[-5:]  # Last 5 messages
        ])

        plan_prompt = f"""基于以下讨论，请生成详细的执行计划：

原始需求：{plan.original_request}
目标输出：{plan.target_output}

讨论摘要：
{discussion_summary}

请以JSON格式输出执行计划，格式如下：
{{
  "title": "计划标题",
  "description": "计划描述",
  "tasks": [
    {{
      "title": "任务标题",
      "description": "任务描述",
      "assigned_agent_type": "coder/analyst/tester/assistant",
      "order": 1
    }}
  ]
}}

确保任务按顺序排列，每个任务明确分配给合适的Agent。"""

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

                # Find the right agent
                if agent_type_str == "coder" and coder:
                    assigned_agent_id = coder.id
                elif agent_type_str == "analyst" and analyst:
                    assigned_agent_id = analyst.id
                elif agent_type_str == "tester" and tester:
                    assigned_agent_id = tester.id
                elif agent_type_str == "assistant" and assistant:
                    assigned_agent_id = assistant.id

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
            plan.tasks = [
                PlanTask(
                    id=str(uuid.uuid4()),
                    title="实现核心功能",
                    description=plan.original_request,
                    assigned_agent_id=coder.id if coder else None,
                    assigned_agent_type="coder",
                    order=1,
                )
            ]

        plan.status = PlanStatus.APPROVED
        plan.updated_at = datetime.utcnow()

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
        """Phase 4: Execute the plan step by step"""
        plan = self.plans.get(plan_id)
        if not plan:
            return "Plan not found"

        plan.status = PlanStatus.EXECUTING
        plan.started_at = datetime.utcnow()

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

        for task in sorted_tasks:
            if not task.assigned_agent_id:
                continue

            agent = agent_manager.get_agent(task.assigned_agent_id)
            if not agent:
                continue

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
            task_description = f"""任务：{task.title}

描述：{task.description or '无详细描述'}

原始需求上下文：{plan.original_request}

请完成你的任务部分，提供详细的输出。"""

            # Execute task
            agent.update_status(AgentStatus.WORKING)
            full_response = ""

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

            task.status = TaskStatus.COMPLETED
            results.append({
                "task": task.title,
                "agent": agent.name,
                "result": full_response,
            })

            agent.update_status(AgentStatus.IDLE)

            await self.broadcast({
                "type": "plan_update",
                "data": {
                    "plan_id": plan_id,
                    "task_id": task.id,
                    "status": "completed",
                    "result": full_response,
                }
            })

        plan.status = PlanStatus.COMPLETED
        plan.completed_at = datetime.utcnow()

        await self.broadcast({
            "type": "plan_update",
            "data": {
                "plan_id": plan_id,
                "status": "completed",
                "results": results,
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
