import asyncio
import importlib
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from app.models.schemas import Plan, PlanTask, TaskStatus, PlanStatus
from app.services.coordinator import CoordinatorService


coordinator_module = importlib.import_module("app.services.coordinator")


class FakeCoderAgent:
    def __init__(self):
        self.id = "coder-1"
        self.name = "Coder Agent"
        self.type = SimpleNamespace(value="coder")
        self.calls = []
        self.status = None

    def update_status(self, status):
        self.status = status

    async def execute_task(self, task_description, existing_code=None, incremental_mode=False, target_output="web-app"):
        self.calls.append(
            {
                "task_description": task_description,
                "existing_code": existing_code,
                "incremental_mode": incremental_mode,
                "target_output": target_output,
            }
        )
        yield {
            "type": "stream",
            "content": """// filename: src/main.ts
const root = document.getElementById('app');
if (!root) throw new Error('Missing root');
root.textContent = 'ready';
""",
        }


@patch.object(CoordinatorService, "_load_plans", return_value=None)
def test_execute_plan_retries_ts_app_when_build_fails(_mock_load_plans, monkeypatch):
    service = CoordinatorService()
    service.broadcast = AsyncMock()
    service.add_discussion_message = AsyncMock()
    service._save_plans = lambda: None

    task = PlanTask(
        id="task-1",
        title="实现主界面",
        description="输出 ts-app 代码",
        assigned_agent_id="coder-1",
        assigned_agent_type="coder",
        status=TaskStatus.PENDING,
        order=1,
    )
    plan = Plan(
        id="plan-ts-1",
        title="TS Plan",
        original_request="做一个 TypeScript 小游戏",
        target_output="ts-app",
        tasks=[task],
        status=PlanStatus.EXECUTING,
    )
    service.plans[plan.id] = plan

    agent = FakeCoderAgent()
    saved_snapshot = {"code": None}
    build_calls = {"count": 0}

    def fake_read_existing_ts_code(_plan_id: str, max_length: int = 20000):
        return saved_snapshot["code"]

    def fake_save_ts_project(*, plan_id: str, task_title: str, content: str):
        saved_snapshot["code"] = content
        return [f"/tmp/{plan_id}/{task_title}.ts"]

    def fake_pretest(_plan_id: str):
        return {"passed": True, "errors": [], "warnings": []}

    def fake_build(*_args, **_kwargs):
        build_calls["count"] += 1
        if build_calls["count"] == 1:
            return {
                "passed": False,
                "command": ["npm", "run", "build"],
                "returncode": 1,
                "errors": ["src/main.ts:3: error TS1005: ';' expected"],
                "warnings": [],
                "project_dir": "/tmp/plan-ts-1/ts_app",
            }
        return {
            "passed": True,
            "command": ["npm", "run", "build"],
            "returncode": 0,
            "errors": [],
            "warnings": [],
            "project_dir": "/tmp/plan-ts-1/ts_app",
        }

    monkeypatch.setattr(coordinator_module.agent_manager, "get_agent", lambda _agent_id: agent)
    monkeypatch.setattr(coordinator_module.output_manager, "read_existing_ts_code", fake_read_existing_ts_code)
    monkeypatch.setattr(coordinator_module.output_manager, "save_ts_project", fake_save_ts_project)
    monkeypatch.setattr(coordinator_module.output_manager, "save_plan_output", lambda **_kwargs: None)
    monkeypatch.setattr(coordinator_module.output_manager, "pre_test_validation_ts_app", fake_pretest)
    monkeypatch.setattr(coordinator_module.output_manager, "build_ts_project", fake_build)
    monkeypatch.setattr(coordinator_module.output_manager, "save_iteration_archive", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(coordinator_module.output_manager, "get_output_path", lambda _plan_id: "/tmp/output/plan-ts-1")
    monkeypatch.setattr(coordinator_module.output_manager, "resolve_preview_entry", lambda *_args, **_kwargs: "ts_app/dist/index.html")
    monkeypatch.setattr(coordinator_module.feedback_store, "get_guidance_for_task", lambda _task: None)
    monkeypatch.setattr(coordinator_module.feedback_store, "get_error_guidance", lambda _code, _task=None: None)
    monkeypatch.setattr(coordinator_module.growth_service, "add_task_score", lambda _agent_id: {"score_gained": 0, "total_score": 0})
    monkeypatch.setattr(
        coordinator_module.growth_service,
        "on_task_completed",
        lambda **_kwargs: {"level_up": False, "xp_gained": 0},
    )

    asyncio.run(service.execute_plan(plan.id))

    assert build_calls["count"] == 2
    assert len(agent.calls) == 2
    assert agent.calls[0]["target_output"] == "ts-app"
    assert agent.calls[1]["target_output"] == "ts-app"
    assert agent.calls[0]["incremental_mode"] is False
    assert agent.calls[1]["incremental_mode"] is True
    assert "TypeScript 工程构建失败" in agent.calls[1]["task_description"]
    assert "TS1005" in agent.calls[1]["task_description"]
    assert plan.tasks[0].status == TaskStatus.COMPLETED
    assert plan.status == PlanStatus.COMPLETED
