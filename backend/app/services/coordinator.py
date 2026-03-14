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
from app.services.agent_growth_service import growth_service
from app.services.motivation_service import motivation_service
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
        # 任务分配计数器：{plan_id: {agent_type: counter}}，用于轮询分配任务
        self._task_assignment_counters: Dict[str, Dict[str, int]] = {}
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

    def _build_agents_by_type(self, selected_agents: List, selected_agent_ids: List[str] = None) -> Dict[str, List]:
        """构建按类型分组的 Agent 列表，支持每类型多个 Agent

        Args:
            selected_agents: 已选择的 Agent 列表
            selected_agent_ids: 用户选择的 Agent ID 顺序（用于保持选择顺序）

        Returns:
            Dict[str, List]: 按类型分组的 Agent 列表，例如 {'coder': [agent1, agent2], 'tester': [agent3]}
        """
        agents_by_type = {}
        sorted_agents = selected_agents

        if selected_agent_ids:
            # 按用户选择的顺序排序
            agent_order = {aid: i for i, aid in enumerate(selected_agent_ids)}
            sorted_agents = sorted(
                [a for a in selected_agents if a.id in agent_order],
                key=lambda a: agent_order.get(a.id, float('inf'))
            )

        for agent in sorted_agents:
            agent_type = agent.type.value if hasattr(agent.type, 'value') else str(agent.type)
            if agent_type not in agents_by_type:
                agents_by_type[agent_type] = []
            agents_by_type[agent_type].append(agent)

        return agents_by_type

    def _get_agent_for_task(self, plan_id: str, agent_type: str, agents_by_type: Dict[str, List]) -> Optional[Any]:
        """轮询方式获取下一个可用的 Agent

        当有多个同类型 Agent 时，使用轮询方式分配任务，确保负载均衡。

        Args:
            plan_id: 计划 ID
            agent_type: Agent 类型（如 'coder', 'tester'）
            agents_by_type: 按类型分组的 Agent 列表

        Returns:
            Agent 对象或 None
        """
        agents = agents_by_type.get(agent_type, [])
        if not agents:
            return None
        if len(agents) == 1:
            return agents[0]

        # 轮询分配
        if plan_id not in self._task_assignment_counters:
            self._task_assignment_counters[plan_id] = {}

        if agent_type not in self._task_assignment_counters[plan_id]:
            self._task_assignment_counters[plan_id][agent_type] = 0

        counter = self._task_assignment_counters[plan_id][agent_type]
        selected_agent = agents[counter % len(agents)]
        self._task_assignment_counters[plan_id][agent_type] = counter + 1

        return selected_agent

    def _infer_web_app_profile(self, request: str = "", existing_code: Optional[str] = None) -> str:
        """Infer the most suitable implementation profile for a web-app task."""
        source = f"{request}\n{existing_code or ''}".lower()

        if "<canvas" in source or "getcontext(" in source or "webgl" in source:
            return "canvas-game"

        canvas_keywords = [
            "canvas", "webgl", "shader", "particle", "physics", "platformer", "shooter",
            "bullet", "arcade", "racing", "flight", "pong", "breakout", "snake", "frame loop"
        ]
        dom_game_keywords = [
            "三消", "match-3", "match3", "2048", "sudoku", "棋盘", "board", "grid", "tile",
            "puzzle", "card", "memory", "inventory", "kanban", "calendar"
        ]
        spa_keywords = [
            "dashboard", "admin", "表单", "form", "settings", "landing", "portfolio", "saas",
            "管理台", "后台", "仪表盘", "博客", "官网", "工具页"
        ]

        if any(keyword in source for keyword in canvas_keywords):
            return "canvas-game"
        if any(keyword in source for keyword in dom_game_keywords):
            return "dom-interactive"
        if any(keyword in source for keyword in spa_keywords):
            return "single-page-app"
        return "dom-interactive"

    def _build_web_app_constraints(
        self,
        request: str,
        existing_code: Optional[str] = None,
        incremental_mode: bool = False,
    ) -> str:
        """Build profile-aware constraints for web-app generation."""
        profile = self._infer_web_app_profile(request, existing_code)
        profile_labels = {
            "canvas-game": "Canvas/WebGL 实时游戏",
            "dom-interactive": "DOM 交互页 / 棋盘类小游戏",
            "single-page-app": "普通单页应用",
        }
        profile_guidance = {
            "canvas-game": "- 优先使用 Canvas/WebGL 与显式渲染循环\n- 需要真实的输入、状态更新与绘制逻辑\n- 只有这类页面才应使用 `getContext()`、`requestAnimationFrame`、逐帧动画",
            "dom-interactive": "- 优先使用语义化 DOM、CSS Grid/Flex 和事件绑定\n- 关键按钮、棋盘/列表、状态区、提示区必须真实存在且可操作\n- 禁止为了迎合模板强行塞入空 canvas、假 game loop 或无意义动画循环",
            "single-page-app": "- 优先使用 DOM 结构、表单、列表、面板和状态切换\n- 交互应真实驱动数据与视图变化，不要只改提示文案\n- 除非需求明确需要逐帧渲染，否则不要引入 canvas 或持续循环",
        }
        mode_note = "- 当前为增量修改任务：保留现有可用功能，只修改与当前任务相关的部分\n- 输出仍必须是完整的最终 HTML，而不是 diff 或补丁" if incremental_mode else "- 当前为首次生成/重构任务：按需求选择最合适的实现模式，不要套错模板"

        return f"""
⚠️ Web应用开发要求（必须全部满足，否则视为未完成任务）：
1. 生成完整的单文件 HTML（包含内联 CSS 和 JavaScript），打开即可运行。
2. 不要引用外部文件（如 js/xxx.js, css/xxx.css），也不要使用 Node.js 特有功能（如 require、module.exports、express、socket.io 等）。
3. 所有功能必须在浏览器中运行；如需数据存储，只能使用 localStorage 或 sessionStorage。
4. 关键控件、状态区、提示区和主交互对象都必须真实存在且可操作，不能只做静态占位。
5. 不要为了迎合模板强行加入无关的 `<canvas>`、`getContext('2d')`、`requestAnimationFrame` 或空的游戏循环。
6. 若本计划中有多个任务分别产出模块，最终必须整合为一个可独立运行的 `index.html`。

【当前推荐实现模式】{profile_labels[profile]}
{profile_guidance[profile]}
{mode_note}
"""

    def _summarize_ts_issues(self, payload: Optional[Dict[str, Any]], stage_label: str) -> str:
        payload = payload or {}
        error_lines = [f"- ❌ {err}" for err in (payload.get("errors") or [])[:8]]
        warning_lines = [f"- ⚠️ {warn}" for warn in (payload.get("warnings") or [])[:3]]
        summary = "\n".join(error_lines + warning_lines).strip()
        return summary or f"- ❌ TypeScript 工程{stage_label}失败"

    def _build_ts_fix_feedback(self, plan_id: str, stage_label: str, payload: Dict[str, Any], task_request: str) -> str:
        summary = self._summarize_ts_issues(payload, stage_label)
        code_snapshot = output_manager.read_existing_ts_code(plan_id, max_length=16000) or ""

        guidance_parts: List[str] = []
        task_guidance = feedback_store.get_guidance_for_task(task_request)
        if task_guidance:
            guidance_parts.append(task_guidance)
        historical_guidance = feedback_store.get_error_guidance(code_snapshot, task_request)
        if historical_guidance and historical_guidance not in guidance_parts:
            guidance_parts.append(historical_guidance)

        guidance_block = ""
        if guidance_parts:
            guidance_block = "\n\n历史修复提醒：\n" + "\n\n".join(guidance_parts)

        return f"""TypeScript 工程{stage_label}失败，请基于当前已有工程做定点修复。

失败详情：
{summary}

修复要求：
- 当前工程快照已经作为 existing_code 提供，请直接在现有文件基础上修复
- 优先处理 errors 中点名的文件与首批报错，避免大面积无关重写
- 只输出本轮需要新增或替换的完整文件，保持 `// filename: src/...` 格式
- 不要输出 package.json、tsconfig.json、vite.config.ts、index.html
- 先修复 TypeScript 语法、类型、import/export 与缺失符号，再重新尝试 Vite build{guidance_block}
"""

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
        """Re-assign agents to tasks after loading (agent IDs may have changed)

        Handles both main plan tasks and iteration tasks to ensure all tasks
        have valid agent assignments after service restart or plan resume.
        """
        plan = self.plans.get(plan_id)
        if not plan:
            return

        # Get current agents, respecting user's selection order
        all_agents = agent_manager.get_all_agents()

        # Build agents_by_type using the shared helper (Dict[str, List[Agent]])
        selected_agent_order = plan.selected_agent_ids
        if plan.selected_agent_ids:
            selected_agents = [a for a in all_agents if a.id in plan.selected_agent_ids]
            # Fallback when stored selected IDs are stale after restart or agent recreation
            if not selected_agents:
                selected_agents = all_agents
                selected_agent_order = None
        else:
            selected_agents = all_agents
            selected_agent_order = None

        agents_by_type = self._build_agents_by_type(selected_agents, selected_agent_order)

        # Helper to reassign a single task
        def reassign_task(task) -> bool:
            """Reassign a task if needed. Returns True if reassigned."""
            if task.assigned_agent_type and task.assigned_agent_type in agents_by_type:
                agent_list = agents_by_type[task.assigned_agent_type]
                if agent_list:
                    agent = agent_list[0]
                    if task.assigned_agent_id != agent.id:
                        task.assigned_agent_id = agent.id
                        return True
            return False

        # Re-assign agents to main plan tasks
        reassigned = 0
        for task in plan.tasks:
            if reassign_task(task):
                reassigned += 1

        # Re-assign agents to iteration tasks
        for iteration in plan.iterations:
            for task in iteration.tasks:
                if reassign_task(task):
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

    async def request_continuation(
        self,
        partial_code: str,
        issues: List[str],
        plan_id: str = None,
        task_id: str = None,
    ) -> str:
        """Request LLM to continue generating truncated code.

        Args:
            partial_code: The incomplete code generated so far
            issues: List of completeness issues detected
            plan_id: Optional plan ID for context
            task_id: Optional task ID for context

        Returns:
            The continuation code to complete the truncated response
        """
        issues_text = '\n'.join(f'- {issue}' for issue in issues)

        prompt = f"""之前的代码生成被截断了，存在以下问题：
{issues_text}

请从截断处继续完成代码。

⚠️ 重要提示：
1. 只输出剩余部分的代码（不要重复已生成的代码）
2. 如果截断处是函数或语句中间，先完成那个函数/语句
3. 确保输出的代码能与之前的部分正确拼接
4. 必须包含闭合标签（如 </script></body></html>）

以下是之前生成的代码最后2000字符，请继续：
```
{partial_code[-2000:]}
```

请继续完成代码："""

        continuation = ""
        try:
            # Notify that we're requesting continuation
            if plan_id:
                await self.broadcast({
                    "type": "stream",
                    "data": {
                        "plan_id": plan_id,
                        "task_id": task_id,
                        "content": "\n\n⚠️ 检测到代码被截断，正在请求继续生成...\n\n",
                    }
                })

            async for chunk in glm_client.chat_stream(prompt, "coder"):
                continuation += chunk
                await self.broadcast({
                    "type": "stream",
                    "data": {
                        "plan_id": plan_id,
                        "task_id": task_id,
                        "content": chunk,
                    }
                })

            print(f"[Coordinator] Continuation generated: {len(continuation)} chars")

        except Exception as e:
            print(f"[Coordinator] Error requesting continuation: {e}")
            # Return a fallback closing
            continuation = "\n\n// [代码生成中断，请重新生成]"

        return continuation

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
        tokens_used: int = 0,
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

        # Add discussion score (skip for system messages)
        if agent_id != "system":
            score_result = growth_service.add_discussion_score(agent_id, tokens_used)
            await self.broadcast({
                "type": "score_update",
                "data": {
                    "agent_id": agent_id,
                    "score_gained": score_result["score_gained"],
                    "total_score": score_result["total_score"],
                    "reason": "discussion"
                }
            })

        return msg

    async def analyze_request(self, plan_id: str) -> str:
        """Phase 1: Assistant analyzes the user request"""
        plan = self.plans.get(plan_id)
        if not plan:
            return "Plan not found"

        # Find the Assistant agent (filtered by selected_agent_ids)
        all_agents = agent_manager.get_all_agents()
        # 根据 selected_agent_ids 过滤
        if plan.selected_agent_ids:
            selected_agents = [a for a in all_agents if a.id in plan.selected_agent_ids]
        else:
            selected_agents = all_agents
        print(f"[Coordinator] Found {len(selected_agents)} selected agents: {[a.name for a in selected_agents]}")

        assistant = None
        for agent in selected_agents:
            if agent.type == AgentType.ASSISTANT:
                assistant = agent
                break

        if not assistant:
            print("[Coordinator] No Assistant agent found in selected agents!")
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

    def _build_discussion_summary(self, plan: Plan) -> str:
        """Build a structured discussion summary for Coder context.

        Extracts key technical points from discussion messages, organized by:
        - Tech stack recommendations
        - Architecture decisions
        - Important warnings/risks
        - Testing considerations
        """
        if not plan.discussion:
            return ""

        # Categorize messages by agent type
        coder_points = []
        analyst_points = []
        tester_points = []
        assistant_points = []

        for msg in plan.discussion:
            content = msg.content.strip()
            if len(content) < 20:  # Skip very short messages
                continue

            if msg.agent_type == "coder":
                coder_points.append(f"- {content[:500]}")  # Limit length
            elif msg.agent_type == "analyst":
                analyst_points.append(f"- {content[:500]}")
            elif msg.agent_type == "tester":
                tester_points.append(f"- {content[:500]}")
            else:
                assistant_points.append(f"- {content[:300]}")

        # Build structured summary
        summary_parts = []

        if coder_points:
            summary_parts.append("## 💻 Coder 建议")
            summary_parts.extend(coder_points[-3:])  # Last 3 points

        if analyst_points:
            summary_parts.append("\n## 📊 Analyst 分析")
            summary_parts.extend(analyst_points[-2:])  # Last 2 points

        if tester_points:
            summary_parts.append("\n## 🧪 Tester 测试建议")
            summary_parts.extend(tester_points[-2:])  # Last 2 points

        if assistant_points:
            summary_parts.append("\n## 📋 Assistant 协调")
            # Only include coordination messages, skip initial greeting
            for point in assistant_points[-2:]:
                if "请针对" not in point and "感谢各位" not in point:
                    summary_parts.append(point)

        return "\n".join(summary_parts)

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
        # 使用辅助方法构建，支持每类型多个 Agent（轮询分配）
        agents_by_type = self._build_agents_by_type(selected_agents, plan.selected_agent_ids)

        assistant.update_status(AgentStatus.WORKING)

        # Build structured discussion summary and store it for Coder context
        plan.discussion_summary = self._build_discussion_summary(plan)

        # Also create a simple summary for plan generation prompt
        discussion_summary = "\n".join([
            f"[{msg.agent_name}]: {msg.content[:300]}..."
            if len(msg.content) > 300 else f"[{msg.agent_name}]: {msg.content}"
            for msg in plan.discussion[-8:]  # Increased from 5 to 8 messages
        ])

        # Build available agent types string for prompt
        available_agent_types = list(agents_by_type.keys())
        agent_types_str = "/".join(available_agent_types)

        # Add constraints for web-app projects
        web_app_constraints = ""
        if plan.target_output == "web-app":
            web_app_constraints = self._build_web_app_constraints(plan.original_request)

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

        ts_app_constraints = ""
        if plan.target_output == "ts-app":
            ts_app_constraints = """
⚠️ 重要约束（TypeScript 工程项目必须遵守）：
1. 目标产物是 Vite + TypeScript 浏览器应用，任务必须围绕 src/ 下的模块化代码展开
2. 禁止规划生成 package.json、tsconfig.json、vite.config.ts、index.html，这些由模板提供
3. 任务应聚焦入口、核心模块、类型定义、样式与交互逻辑，尽量控制在 3-5 个任务内
4. 代码必须可编译，采用 ES Module 与 TypeScript strict 模式
5. 如果是游戏或交互应用，优先使用原生 Canvas API 与浏览器事件

任务示例（正确）：
- "应用入口与挂载流程" - 实现 src/main.ts 和初始化流程
- "核心玩法与状态管理" - 拆分 game.ts / app.ts 等模块
- "类型定义与工具函数" - 抽离 types.ts、utils.ts

任务示例（错误，禁止）：
- "配置 Vite 构建环境" ❌ (模板已提供)
- "手写 package.json" ❌ (模板已提供)
- "新增后端 API 服务" ❌ (目标是浏览器端 ts-app)
"""

        plan_prompt = f"""基于以下讨论，请生成详细的执行计划：

原始需求：{plan.original_request}
目标输出：{plan.target_output}
{web_app_constraints}{godot_constraints}{ts_app_constraints}
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
                    # 使用轮询方式分配 Agent，支持多个同类型 Agent
                    assigned_agent = self._get_agent_for_task(plan_id, agent_type_str, agents_by_type)
                    assigned_agent_id = assigned_agent.id if assigned_agent else None

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
            # agents_by_type 现在是 {type: [agents]}，取第一个可用 agent
            coder_agents = agents_by_type.get("coder", [])
            assistant_agents = agents_by_type.get("assistant", [])
            fallback_agent = coder_agents[0] if coder_agents else (assistant_agents[0] if assistant_agents else (selected_agents[0] if selected_agents else None))
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
        if plan.target_output == "web-app":
            existing_code = output_manager.read_existing_code(plan_id)
            if existing_code:
                first_coding_task_completed = True
        elif plan.target_output == "ts-app":
            existing_code = output_manager.read_existing_ts_code(plan_id)
            if existing_code:
                first_coding_task_completed = True

        all_tests_passed = True
        test_feedback: List[str] = []
        blocking_reason: Optional[str] = None
        latest_fix_feedback = ""

        while fix_iteration < max_fix_iterations:
            all_tests_passed = True
            blocking_reason = None

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
                        if latest_fix_feedback:
                            fix_context = f"\n\n⚠️ 上一轮自动校验/构建发现问题，请优先修复以下问题：\n{latest_fix_feedback}"
                        else:
                            feedback_results = [
                                r for r in results
                                if any(keyword in r.get('task', '') for keyword in ('测试', '验证', '构建'))
                            ]
                            if feedback_results:
                                fix_context = f"\n\n⚠️ 之前的测试发现问题，请修复以下问题：\n{feedback_results[-1].get('result', '')}"

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
                    existing_code = None
                    incremental_mode = False

                    if plan.target_output == "web-app" and agent.type.value == "coder" and first_coding_task_completed:
                        existing_code = output_manager.read_existing_code(plan_id)
                        if existing_code:
                            incremental_mode = True
                            print(f"[Coordinator] Using incremental mode for task: {task.title} (existing code: {len(existing_code)} chars)")
                    elif plan.target_output == "ts-app" and agent.type.value == "coder" and first_coding_task_completed:
                        existing_code = output_manager.read_existing_ts_code(plan_id)
                        if existing_code:
                            incremental_mode = True
                            print(f"[Coordinator] Using ts-app incremental mode for task: {task.title} (existing code: {len(existing_code)} chars)")

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

                    ts_app_instructions = ""
                    if plan.target_output == "ts-app" and agent.type.value == "coder":
                        if incremental_mode:
                            ts_app_instructions = """

⚠️ TypeScript 工程增量模式（重要）：
- 当前已有一个可编译的 ts_app 工程，你需要在现有 src/ 模块基础上继续修改
- 只输出本轮需要新增或替换的完整文件
- 每个文件必须以 `// filename: src/...` 标注，后面直接跟完整文件内容
- 不要输出 package.json、tsconfig.json、vite.config.ts、index.html
- 保持现有 import/export 关系可编译，不要破坏已有入口"""
                        else:
                            ts_app_instructions = """

⚠️ TypeScript 工程开发要求（必须全部满足，否则视为未完成任务）：
1. 目标是 Vite + TypeScript 浏览器应用，输出多文件源码而不是单文件 HTML。
2. 输出格式：每个文件必须以 `// filename: src/xxx.ts` 或 `// filename: src/xxx.css` 开头。
3. 至少包含可运行入口 `src/main.ts`，并通过真实 DOM 节点挂载应用。
4. 所有代码必须满足 TypeScript strict 模式，使用 ES Module import/export。
5. 禁止输出模板文件（package.json、tsconfig.json、vite.config.ts、index.html），它们已由系统预置。
6. 禁止使用未声明依赖、空函数、TODO、伪代码或 markdown 代码块。

✅ 推荐拆分：入口(main.ts) / 核心逻辑(game.ts|app.ts) / 类型(types.ts) / 样式(styles.css)
✅ 若是互动页面或游戏，优先使用原生 Canvas API 与浏览器事件"""

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

                    # Add discussion summary context for Coders
                    discussion_context = ""
                    if agent.type.value == "coder" and plan.discussion_summary:
                        discussion_context = f"""

💡 团队讨论摘要（供参考）：
{plan.discussion_summary}
"""

                    task_description = f"""任务：{task.title}

描述：{task.description or '无详细描述'}

原始需求上下文：{plan.original_request}
{discussion_context}{previous_tasks_context}{fix_context}{web_app_instructions}{ts_app_instructions}{godot_instructions}

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
                                    incremental_mode=incremental_mode,
                                    target_output=plan.target_output,
                                ):
                                    if update["type"] == "stream":
                                        # Skip empty or whitespace-only content
                                        content = update["content"]
                                        if content and content.strip():
                                            full_response += content
                                            await self.broadcast({
                                                "type": "stream",
                                                "data": {
                                                    "plan_id": plan_id,
                                                    "task_id": task.id,
                                                    "agent_id": agent.id,
                                                    "content": content,
                                                }
                                            })

                            await asyncio.wait_for(execute_with_timeout(), timeout=task_timeout)

                            # Task completed successfully - now check for truncation
                            task_success = True

                            # Check code completeness for coder tasks
                            if agent.type.value == "coder" and full_response:
                                completeness = output_manager.validate_code_completeness(full_response)
                                if not completeness["is_complete"]:
                                    print(f"[Pipeline] Truncation detected in task: {task.title}")
                                    print(f"[Pipeline] Issues: {completeness['issues']}")

                                    # Request continuation from LLM
                                    continuation = await self.request_continuation(
                                        partial_code=full_response,
                                        issues=completeness["issues"],
                                        plan_id=plan_id,
                                        task_id=task.id,
                                    )

                                    if continuation and continuation.strip():
                                        full_response += continuation

                                        # Re-check after continuation
                                        new_completeness = output_manager.validate_code_completeness(full_response)
                                        if new_completeness["is_complete"]:
                                            print(f"[Pipeline] Code completed successfully after continuation")
                                        else:
                                            print(f"[Pipeline] Code still incomplete after continuation: {new_completeness['issues']}")
                                            await self.add_discussion_message(
                                                plan_id=plan_id,
                                                agent_id=agent.id,
                                                agent_name=agent.name,
                                                agent_type=agent.type.value,
                                                content=f"⚠️ 代码可能不完整：{', '.join(completeness['issues'])}",
                                                message_type="comment",
                                            )

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
                        if not first_coding_task_completed:
                            first_coding_task_completed = True
                            print(f"[Coordinator] First coding task completed, incremental mode enabled for subsequent tasks")
                    elif plan.target_output == "ts-app" and task.assigned_agent_type == "coder":
                        saved_files = output_manager.save_ts_project(
                            plan_id=plan_id,
                            task_title=task.title,
                            content=full_response,
                        )
                        if not first_coding_task_completed:
                            first_coding_task_completed = True
                            print(f"[Coordinator] First ts-app coding task completed, incremental mode enabled for subsequent tasks")
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

                # Add task completion score
                score_result = growth_service.add_task_score(agent.id)
                await self.broadcast({
                    "type": "score_update",
                    "data": {
                        "agent_id": agent.id,
                        "score_gained": score_result["score_gained"],
                        "total_score": score_result["total_score"],
                        "reason": "task_completion",
                        "task_title": task.title
                    }
                })

                # Add XP for task completion (handles leveling and achievements)
                xp_result = growth_service.on_task_completed(
                    agent_id=agent.id,
                    quality_grade="B",  # Default grade
                    quality_score=0.7,
                    retries=task_retry_count,
                    complexity=1
                )
                if xp_result.get("level_up"):
                    await self.broadcast({
                        "type": "level_up",
                        "data": {
                            "agent_id": agent.id,
                            "agent_name": agent.name,
                            "new_level": xp_result["new_level"],
                            "xp_gained": xp_result["xp_gained"]
                        }
                    })
                    print(f"[Pipeline] Agent {agent.name} leveled up to {xp_result['new_level']}!")

            # Save combined output for testing
            try:
                output_manager.save_plan_output(
                    plan_id=plan_id,
                    plan_title=plan.title,
                    tasks=[t.model_dump() for t in plan.tasks],
                    target_output=plan.target_output or "web-app",
                )
                if plan.target_output == "web-app":
                    output_manager.consolidate_web_app(plan_id, plan.title)
                    print(f"[OutputManager] Consolidated web app for plan {plan_id[:8]}")
                if plan.target_output == "godot-game":
                    output_manager.consolidate_godot_project(plan_id, plan.title)
                    print(f"[OutputManager] Consolidated Godot project for plan {plan_id[:8]}")
                if plan.target_output == "ts-app":
                    print(f"[OutputManager] Deferred ts-app build until pre-test validation passes for plan {plan_id[:8]}")
            except Exception as e:
                print(f"[OutputManager] Error saving plan output: {e}")

            # ===== Quality Scoring Gate =====
            if plan.target_output in {"web-app", "ts-app"}:
                try:
                    print(f"[Coordinator] Running quality scoring...")
                    validation_payload = None
                    if plan.target_output == "ts-app":
                        existing_code = output_manager.read_existing_ts_code(plan_id)
                        ts_app_dir = output_manager.init_ts_app_project(plan_id)
                        validation_payload = output_manager.web_validator.validate_ts_project(
                            ts_app_dir,
                            stage="quality",
                            requirements=plan.original_request,
                        ).to_dict()
                        quality_result = quality_scorer.score_ts_output(existing_code or "", plan.original_request, validation_payload)
                    else:
                        existing_code = output_manager.read_existing_code(plan_id)
                        quality_result = quality_scorer.score_output(existing_code or "", plan.original_request)

                    if existing_code:
                        print(f"[QualityScorer] Score: {quality_result['total']:.1f}/100 (Grade: {quality_result['grade']})")

                        if not hasattr(plan, 'quality_scores'):
                            plan.quality_scores = []
                        plan.quality_scores.append({
                            "round": fix_iteration,
                            "score": quality_result["total"],
                            "grade": quality_result["grade"],
                            "timestamp": datetime.now().isoformat(),
                            "target_output": plan.target_output,
                        })

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

                            for check in quality_result['scores']['correctness'].get('checks', []):
                                if not check.get('passed', True):
                                    feedback_store.record_error(
                                        plan_id=plan_id,
                                        error_type=check.get('name', 'unknown'),
                                        description=check.get('name', 'Unknown error'),
                                        code_snippet=(existing_code or '')[:500],
                                        task_context=plan.original_request[:200],
                                    )

                            if quality_result["total"] < 40:
                                latest_fix_feedback = quality_feedback
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
                        error_lines = [f"- ❌ {err}" for err in validation.get("errors", [])]
                        warning_lines = [f"- ⚠️ {warn}" for warn in validation.get("warnings", [])[:3]]
                        validation_summary = "\n".join(error_lines + warning_lines)
                        if not validation_summary:
                            validation_summary = "- ❌ 未知校验失败"

                        await self.add_discussion_message(
                            plan_id=plan_id,
                            agent_id="system",
                            agent_name="系统",
                            agent_type="assistant",
                            content=f"⚠️ 预测试验证失败\n\n{validation_summary}\n\n请修复这些问题后重新生成。",
                            message_type="comment",
                        )
                        results.append({
                            "task": "预测试验证",
                            "agent": "system",
                            "result": validation_summary,
                        })
                        latest_fix_feedback = validation_summary
                        test_feedback.append(validation_summary)
                        all_tests_passed = False
                        print(f"[Coordinator] Pre-test validation failed, entering fix loop")

                        if fix_iteration >= max_fix_iterations - 1:
                            blocking_reason = "预测试验证连续失败，已阻断完成态"
                            break

                        fix_iteration += 1
                        await self.add_discussion_message(
                            plan_id=plan_id,
                            agent_id="system",
                            agent_name="系统",
                            agent_type="assistant",
                            content=f"🔄 预测试未通过，开始第 {fix_iteration} 轮修复...\n\n问题摘要：\n{validation_summary}",
                            message_type="comment",
                        )
                        for retry_task in coding_tasks:
                            if retry_task.assigned_agent_type == "coder":
                                retry_task.status = TaskStatus.PENDING
                        self._save_plans()
                        continue
                except Exception as e:
                    print(f"[Coordinator] Pre-test validation failed with error: {e}")
                    # Continue with execution even if validation fails

            if plan.target_output == "ts-app":
                try:
                    print(f"[Coordinator] Running ts-app pre-test validation...")
                    validation = output_manager.pre_test_validation_ts_app(plan_id)

                    if not validation["passed"]:
                        validation_summary = self._summarize_ts_issues(validation, "预测试校验")
                        latest_fix_feedback = self._build_ts_fix_feedback(
                            plan_id,
                            "预测试校验",
                            validation,
                            plan.original_request,
                        )

                        await self.add_discussion_message(
                            plan_id=plan_id,
                            agent_id="system",
                            agent_name="系统",
                            agent_type="assistant",
                            content=f"⚠️ TypeScript 工程预测试验证失败\n\n{validation_summary}\n\n请基于当前工程定点修复这些编译问题后重新生成。",
                            message_type="comment",
                        )
                        results.append({
                            "task": "TypeScript 预测试验证",
                            "agent": "system",
                            "result": validation_summary,
                        })
                        test_feedback.append(validation_summary)
                        all_tests_passed = False
                        print(f"[Coordinator] ts-app pre-test validation failed, entering fix loop")

                        if fix_iteration >= max_fix_iterations - 1:
                            blocking_reason = "TypeScript 工程预测试验证连续失败，已阻断完成态"
                            break

                        fix_iteration += 1
                        await self.add_discussion_message(
                            plan_id=plan_id,
                            agent_id="system",
                            agent_name="系统",
                            agent_type="assistant",
                            content=f"🔄 TypeScript 工程预测试未通过，开始第 {fix_iteration} 轮修复...\n\n问题摘要：\n{validation_summary}",
                            message_type="comment",
                        )
                        for retry_task in coding_tasks:
                            if retry_task.assigned_agent_type == "coder":
                                retry_task.status = TaskStatus.PENDING
                        self._save_plans()
                        continue

                    build_payload = output_manager.build_ts_project(plan_id, plan.title)
                    if not build_payload.get("passed"):
                        build_summary = self._summarize_ts_issues(build_payload, "构建")
                        latest_fix_feedback = self._build_ts_fix_feedback(
                            plan_id,
                            "构建",
                            build_payload,
                            plan.original_request,
                        )

                        await self.add_discussion_message(
                            plan_id=plan_id,
                            agent_id="system",
                            agent_name="系统",
                            agent_type="assistant",
                            content=f"⚠️ TypeScript 工程构建失败\n\n{build_summary}\n\n请基于当前工程定点修复这些构建问题后重新生成。",
                            message_type="comment",
                        )
                        results.append({
                            "task": "TypeScript 构建验证",
                            "agent": "system",
                            "result": build_summary,
                        })
                        test_feedback.append(build_summary)
                        all_tests_passed = False
                        print(f"[Coordinator] ts-app build failed, entering fix loop")

                        if fix_iteration >= max_fix_iterations - 1:
                            blocking_reason = "TypeScript 工程构建连续失败，已阻断完成态"
                            break

                        fix_iteration += 1
                        await self.add_discussion_message(
                            plan_id=plan_id,
                            agent_id="system",
                            agent_name="系统",
                            agent_type="assistant",
                            content=f"🔄 TypeScript 工程构建未通过，开始第 {fix_iteration} 轮修复...\n\n问题摘要：\n{build_summary}",
                            message_type="comment",
                        )
                        for retry_task in coding_tasks:
                            if retry_task.assigned_agent_type == "coder":
                                retry_task.status = TaskStatus.PENDING
                        self._save_plans()
                        continue

                    latest_fix_feedback = ""
                    print(f"[Coordinator] ts-app build passed for plan {plan_id[:8]}")
                except Exception as e:
                    print(f"[Coordinator] ts-app validation/build failed with error: {e}")

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
            for task in testing_tasks:
                # Auto-assign tester agent if not assigned or agent not found
                # 根据 plan.selected_agent_ids 过滤
                all_agents = agent_manager.get_all_agents()
                if plan.selected_agent_ids:
                    available_testers = [a for a in all_agents if a.type.value == 'tester' and a.id in plan.selected_agent_ids]
                else:
                    available_testers = [a for a in all_agents if a.type.value == 'tester']

                if not task.assigned_agent_id:
                    # Find an available tester agent
                    if available_testers:
                        task.assigned_agent_id = available_testers[0].id
                        self._save_plans()

                agent = agent_manager.get_agent(task.assigned_agent_id)
                if not agent:
                    # Try to find any tester agent as fallback
                    if available_testers:
                        agent = available_testers[0]
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

                validation_report = output_manager.read_web_validation(plan_id)
                smoke_report = output_manager.read_web_smoke(plan_id)
                validation_context = ""
                if validation_report:
                    validation_context += "\n\n【结构化校验】\n"
                    validation_context += f"- passed: {validation_report.get('passed', True)}\n"
                    validation_context += f"- profile: {(validation_report.get('signals') or {}).get('profile', 'unknown')}\n"
                    for err in validation_report.get('errors', [])[:5]:
                        validation_context += f"- error: {err}\n"
                    for warn in validation_report.get('warnings', [])[:5]:
                        validation_context += f"- warning: {warn}\n"
                if smoke_report:
                    validation_context += "\n【最小DOM Smoke】\n"
                    validation_context += f"- passed: {smoke_report.get('passed', True)}\n"
                    if smoke_report.get('skipped'):
                        validation_context += f"- skipped: {smoke_report.get('reason', 'yes')}\n"
                    elif smoke_report.get('error'):
                        validation_context += f"- error: {smoke_report.get('error')}\n"

                test_prompt = f"""作为测试工程师，请对生成的代码进行实际验证。

原始需求：{plan.original_request}
{tech_stack_info}{validation_context}

测试任务：{task.title}
{code_context}

⚠️ 重要：首先识别代码使用的技术栈，只测试实际使用的技术，不要假设需要未使用的框架。
⚠️ 重要：上面的结构化校验与 smoke 结果优先级高于主观猜测；若机器校验已失败，请围绕失败点补充验证与修复建议。

请执行以下测试步骤：
1. 结合结构化校验结果确认页面是否具备可运行前提
2. 验证核心功能逻辑是否正确实现
3. 验证边界情况、提示文案与真实行为是否一致

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
        preview_entry = None
        if output_dir:
            preview_entry = output_manager.resolve_preview_entry(plan_id, plan.target_output)
            preview_url = f"/api/pipeline/output/{plan_id}/files/{preview_entry}" if preview_entry else None
            result_emoji = "🎉" if all_tests_passed else "⚠️"
            status_text = "所有测试通过！" if all_tests_passed else (blocking_reason or f"经过 {fix_iteration + 1} 轮修复后完成")
            preview_text = f"🌐 预览地址: http://localhost:8000{preview_url}\n\n点击链接查看生成的网页。" if preview_url else "🌐 当前没有可用预览，请检查构建与校验结果。"
            result_title = "项目已完成！" if all_tests_passed else "项目执行结束，但仍有待修复问题"
            result_message = f"{result_emoji} {result_title}\n\n📊 状态: {status_text}\n\n📦 输出目录: {output_dir}\n\n{preview_text}"
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
                "output_url": f"/api/pipeline/output/{plan_id}/files/{preview_entry}" if output_dir and preview_entry else None,
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
        if plan.target_output == "ts-app":
            existing_code = output_manager.read_existing_ts_code(plan_id)
        else:
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

        # 找到 Assistant Agent（根据 selected_agent_ids 过滤）
        all_agents = agent_manager.get_all_agents()
        if plan.selected_agent_ids:
            selected_agents = [a for a in all_agents if a.id in plan.selected_agent_ids]
        else:
            selected_agents = all_agents
        assistant = next((a for a in selected_agents if a.type == AgentType.ASSISTANT), None)
        if not assistant:
            assistant = selected_agents[0] if selected_agents else None

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

        # 构建 agent 类型映射，使用辅助方法支持每类型多个 Agent
        agents_by_type = self._build_agents_by_type(selected_agents, plan.selected_agent_ids)

        assistant.update_status(AgentStatus.WORKING)

        # 编译讨论摘要
        discussion_summary = "\n".join([
            f"[{msg.agent_name}]: {msg.content}"
            for msg in iteration_round.discussion[-5:]
        ])

        # 获取可用的 agent 类型
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
                    # 使用轮询方式分配 Agent，支持多个同类型 Agent
                    assigned_agent = self._get_agent_for_task(plan_id, agent_type_str, agents_by_type)
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
            # agents_by_type 现在是 {type: [agents]}，取第一个可用 agent
            coder_agents = agents_by_type.get("coder", [])
            assistant_agents = agents_by_type.get("assistant", [])
            fallback_agent = coder_agents[0] if coder_agents else (assistant_agents[0] if assistant_agents else (selected_agents[0] if selected_agents else None))

            # 如果还是没有 agent，从选中的 agent 中找一个
            if not fallback_agent:
                if plan.selected_agent_ids:
                    all_agents_list = agent_manager.get_all_agents()
                    selected_fallback = [a for a in all_agents_list if a.id in plan.selected_agent_ids]
                    fallback_agent = next((a for a in selected_fallback if a.type == AgentType.CODER), None)
                    if not fallback_agent:
                        fallback_agent = selected_fallback[0] if selected_fallback else None
                else:
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

            # 构建迭代任务描述 - 使用目标输出对应的增量修改格式
            if plan.target_output == "ts-app":
                iteration_prompt = f"""你是专业的 TypeScript 工程开发工程师。现在需要对现有 ts-app 工程进行**增量修改**。

## 原始需求
{plan.original_request}

## 迭代需求
{iteration_round.iteration_request}

## 当前任务
{task.title}
{task.description or ''}

## 现有工程快照（仅供理解结构）
```
{code_preview}
```

## 🎯 输出格式要求（必须严格遵守）

### 第一步：分析（必须）
简要说明：
- 你要修改哪些文件
- 每个文件为什么要改
- 修改后如何满足迭代需求

### 第二步：输出文件块
只输出发生变化的完整文件，使用以下格式：

<<<FILE: src/main.ts>>>
// 该文件的完整最新内容
<<<END_FILE>>>

<<<FILE: src/styles.css>>>
/* 该文件的完整最新内容 */
<<<END_FILE>>>

如果需要删除文件，使用：
<<<DELETE_FILE: src/obsolete.ts>>>
<<<END_FILE>>>

### ⚠️ 重要规则
1. 只输出变更文件，不要重复未修改文件
2. 每个 FILE 块必须是**完整文件内容**，不能只给局部 diff
3. 路径只能放在 src/ 或 public/ 下
4. 不要输出 markdown 代码块包裹文件内容
5. 保持 import/export 路径正确，可直接被 Vite + TypeScript 工程使用
6. 如果改动较大，可以一次输出多个 FILE 块

请先分析，然后输出文件块。"""
            else:
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
                    modifications = code_merger.parse_modifications(full_response)
                    if modifications:
                        if plan.target_output == "ts-app":
                            merge_result = code_merger.merge_ts_project(current_code, modifications)
                        else:
                            merge_result = code_merger.merge_html(current_code, modifications)
                        current_code = merge_result.code
                        code_updated = merge_result.applied > 0

                        print(f"[Iteration] Applied {merge_result.applied}/{len(modifications)} modifications")
                        if merge_result.failed:
                            print(f"[Iteration] Failed modifications: {merge_result.failed}")

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

                if not code_updated and plan.target_output == "ts-app":
                    extracted_files = output_manager.extract_ts_app_files(full_response)
                    if extracted_files:
                        current_code = "\n\n".join(
                            f"// filename: {file_info['path']}\n{file_info['content']}\n"
                            for file_info in extracted_files
                        ).strip()
                        code_updated = True
                        print("[Iteration] Using ts-app full file replacement (fallback mode)")

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
                    if plan.target_output == "ts-app":
                        try:
                            output_manager.save_ts_project(plan_id, task.title, current_code)
                            validation = output_manager.pre_test_validation_ts_app(plan_id)
                            if validation.get("passed"):
                                build_payload = output_manager.build_ts_project(plan_id, plan.title)
                                if build_payload.get("passed"):
                                    task.status = TaskStatus.COMPLETED
                                    await self._add_iteration_discussion_message(
                                        plan_id, iteration_round.round_number,
                                        agent_id=agent.id,
                                        agent_name=agent.name,
                                        agent_type=agent.type.value,
                                        content=f"✅ 完成任务：{task.title}",
                                        message_type="comment",
                                    )
                                else:
                                    task.status = TaskStatus.FAILED
                                    build_summary = self._summarize_ts_issues(build_payload, "构建")
                                    await self._add_iteration_discussion_message(
                                        plan_id, iteration_round.round_number,
                                        agent_id=agent.id,
                                        agent_name=agent.name,
                                        agent_type=agent.type.value,
                                        content=f"❌ TypeScript 工程构建失败：\n{build_summary}\n\n请重新输出只包含修复文件的完整文件块。",
                                        message_type="comment",
                                    )
                            else:
                                task.status = TaskStatus.FAILED
                                validation_summary = self._summarize_ts_issues(validation, "校验")
                                await self._add_iteration_discussion_message(
                                    plan_id, iteration_round.round_number,
                                    agent_id=agent.id,
                                    agent_name=agent.name,
                                    agent_type=agent.type.value,
                                    content=f"❌ TypeScript 工程校验失败：\n{validation_summary}\n\n请重新输出可编译的完整文件块。",
                                    message_type="comment",
                                )
                        except Exception as e:
                            task.status = TaskStatus.FAILED
                            print(f"[Coordinator] Error saving ts-app iteration code: {e}")
                            await self._add_iteration_discussion_message(
                                plan_id, iteration_round.round_number,
                                agent_id=agent.id,
                                agent_name=agent.name,
                                agent_type=agent.type.value,
                                content=f"❌ TypeScript 工程保存失败：{e}",
                                message_type="comment",
                            )
                    else:
                        is_html_content = current_code.strip().lower().startswith('<!doctype') or \
                                       current_code.strip().lower().startswith('<html')

                        if is_html_content:
                            is_complete, error_msg = self._validate_html_completeness(current_code)
                            if is_complete:
                                task.status = TaskStatus.COMPLETED

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

        preview_entry = output_manager.resolve_preview_entry(plan_id, plan.target_output)
        preview_url = f"/api/pipeline/output/{plan_id}/files/{preview_entry}" if preview_entry else None
        preview_message = f"🎉 迭代第 {iteration_round.round_number} 轮完成！\n\n🌐 预览地址: http://localhost:8000{preview_url}" if preview_url else f"🎉 迭代第 {iteration_round.round_number} 轮完成！\n\n当前没有可用预览，请检查构建结果。"
        await self._add_iteration_discussion_message(
            plan_id, iteration_round.round_number,
            agent_id="system",
            agent_name="系统",
            agent_type="assistant",
            content=preview_message,
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
