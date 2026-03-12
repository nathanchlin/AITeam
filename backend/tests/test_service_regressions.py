"""Regression tests for coordinator reassignment and markdown code extraction."""
import importlib
from types import SimpleNamespace
from unittest.mock import patch

from app.models.schemas import AgentType, Plan, PlanTask
from app.services.coordinator import CoordinatorService
from app.services.output_manager import OutputManager


coordinator_module = importlib.import_module("app.services.coordinator")



def make_agent(agent_id: str, name: str, agent_type: AgentType):
    return SimpleNamespace(id=agent_id, name=name, type=agent_type)



def make_plan(tasks, selected_agent_ids=None) -> Plan:
    return Plan(
        id="plan-1",
        title="Regression Plan",
        original_request="Validate regression behavior",
        target_output="web-app",
        tasks=tasks,
        selected_agent_ids=selected_agent_ids or [],
    )


@patch.object(CoordinatorService, "_load_plans", return_value=None)
def test_reassign_agents_uses_first_agent_in_selected_order(_mock_load_plans):
    service = CoordinatorService()
    task = PlanTask(
        id="task-1",
        title="Implement feature",
        assigned_agent_id="legacy-coder",
        assigned_agent_type="coder",
        order=1,
    )
    plan = make_plan([task], selected_agent_ids=["coder-b", "tester-a", "coder-a"])
    service.plans[plan.id] = plan

    agents = [
        make_agent("coder-a", "Coder A", AgentType.CODER),
        make_agent("tester-a", "Tester A", AgentType.TESTER),
        make_agent("coder-b", "Coder B", AgentType.CODER),
    ]

    with patch.object(service, "_save_plans") as mock_save, patch.object(
        coordinator_module.agent_manager, "get_all_agents", return_value=agents
    ):
        service._reassign_agents(plan.id)

    assert plan.tasks[0].assigned_agent_id == "coder-b"
    mock_save.assert_called_once()


@patch.object(CoordinatorService, "_load_plans", return_value=None)
def test_reassign_agents_falls_back_when_selected_ids_are_stale(_mock_load_plans):
    service = CoordinatorService()
    tasks = [
        PlanTask(
            id="task-1",
            title="Code task",
            assigned_agent_id="old-coder",
            assigned_agent_type="coder",
            order=1,
        ),
        PlanTask(
            id="task-2",
            title="Test task",
            assigned_agent_id="old-tester",
            assigned_agent_type="tester",
            order=2,
        ),
    ]
    plan = make_plan(tasks, selected_agent_ids=["missing-coder", "missing-tester"])
    service.plans[plan.id] = plan

    agents = [
        make_agent("new-coder", "Coder", AgentType.CODER),
        make_agent("new-tester", "Tester", AgentType.TESTER),
    ]

    with patch.object(service, "_save_plans") as mock_save, patch.object(
        coordinator_module.agent_manager, "get_all_agents", return_value=agents
    ):
        service._reassign_agents(plan.id)

    assert plan.tasks[0].assigned_agent_id == "new-coder"
    assert plan.tasks[1].assigned_agent_id == "new-tester"
    mock_save.assert_called_once()


@patch.object(CoordinatorService, "_load_plans", return_value=None)
def test_reassign_agents_skips_tasks_without_available_agent_type(_mock_load_plans):
    service = CoordinatorService()
    task = PlanTask(
        id="task-1",
        title="Unknown task",
        assigned_agent_id="legacy-tester",
        assigned_agent_type="tester",
        order=1,
    )
    plan = make_plan([task], selected_agent_ids=[])
    service.plans[plan.id] = plan

    agents = [make_agent("coder-a", "Coder A", AgentType.CODER)]

    with patch.object(service, "_save_plans") as mock_save, patch.object(
        coordinator_module.agent_manager, "get_all_agents", return_value=agents
    ):
        service._reassign_agents(plan.id)

    assert plan.tasks[0].assigned_agent_id == "legacy-tester"
    mock_save.assert_not_called()



def test_extract_code_blocks_accepts_standard_fenced_block(tmp_path):
    manager = OutputManager(base_dir=str(tmp_path))

    blocks = manager.extract_code_blocks("Before\n```python\nprint('hi')\n```\nAfter")

    assert len(blocks) == 1
    assert blocks[0]["language"] == "python"
    assert blocks[0]["filename"] == "code.py"
    assert blocks[0]["code"] == "print('hi')"



def test_extract_code_blocks_allows_spaces_and_tabs_after_language(tmp_path):
    manager = OutputManager(base_dir=str(tmp_path))

    blocks = manager.extract_code_blocks("```html \t\n<div>ok</div>\n```")

    assert len(blocks) == 1
    assert blocks[0]["language"] == "html"
    assert blocks[0]["filename"] == "index.html"
    assert blocks[0]["code"] == "<div>ok</div>"



def test_extract_code_blocks_defaults_to_text_without_language(tmp_path):
    manager = OutputManager(base_dir=str(tmp_path))

    blocks = manager.extract_code_blocks("```\nplain text\n```")

    assert len(blocks) == 1
    assert blocks[0]["language"] == "text"
    assert blocks[0]["code"] == "plain text"



def test_extract_code_blocks_rejects_inline_fence_without_newline(tmp_path):
    manager = OutputManager(base_dir=str(tmp_path))

    blocks = manager.extract_code_blocks("Prefix ```html<div>bad</div>``` suffix")

    assert blocks == []
