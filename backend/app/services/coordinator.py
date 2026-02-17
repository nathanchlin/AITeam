import asyncio
import os
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid
import json
from app.services.agent_manager import agent_manager
from app.services.output_manager import output_manager
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
        """Phase 4: Execute the plan step by step with testing and feedback loop"""
        plan = self.plans.get(plan_id)
        if not plan:
            return "Plan not found"

        plan.status = PlanStatus.EXECUTING
        plan.started_at = datetime.utcnow()

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
        coding_tasks = [t for t in sorted_tasks if t.assigned_agent_type in ['coder', 'analyst', 'assistant']]
        testing_tasks = [t for t in sorted_tasks if t.assigned_agent_type == 'tester']

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

                # Post task start to group chat
                await self.add_discussion_message(
                    plan_id=plan_id,
                    agent_id=agent.id,
                    agent_name=agent.name,
                    agent_type=agent.type.value,
                    content=f"📝 开始任务：{task.title}",
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

                task_description = f"""任务：{task.title}

描述：{task.description or '无详细描述'}

原始需求上下文：{plan.original_request}
{fix_context}
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
                try:
                    index_path = os.path.join(output_dir, "index.html")
                    if os.path.exists(index_path):
                        with open(index_path, 'r', encoding='utf-8') as f:
                            code_content = f.read()
                            # Include key parts of the code for testing
                            code_context = f"\n\n生成的代码（关键部分）：\n```html\n{code_content[:3000]}...\n```\n"
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
