"""
Unit tests for CoordinatorService._reassign_agents() covering main tasks and iteration tasks.

Tests verify that agent reassignment works correctly for:
1. Main plan tasks
2. Iteration tasks
3. Stale selected_agent_ids fallback
4. Multiple agents of same type
5. Missing agent type scenarios
"""

import importlib
from types import SimpleNamespace
from unittest.mock import patch

from app.services.coordinator import CoordinatorService
from app.models.schemas import (
    Plan,
    PlanTask,
    IterationTask,
    IterationRound,
    TaskStatus,
    AgentType,
)


coordinator_module = importlib.import_module("app.services.coordinator")


def make_agent(agent_id: str, name: str, agent_type: str):
    """Helper to create agent-like object for testing."""
    # Convert string to AgentType enum
    type_enum = AgentType(agent_type) if isinstance(agent_type, str) else agent_type
    return SimpleNamespace(id=agent_id, name=name, type=type_enum)


@patch.object(CoordinatorService, "_load_plans", return_value=None)
def test_reassign_agents_handles_main_plan_tasks(_mock_load_plans):
    """Main plan tasks should be reassigned when agent IDs change."""
    service = CoordinatorService()
    
    task = PlanTask(
        id="task-1",
        title="Test Task",
        assigned_agent_id="old-coder-id",
        assigned_agent_type="coder",
        status=TaskStatus.PENDING,
    )
    
    plan = Plan(
        id="plan-1",
        title="Test Plan",
        original_request="test",
        tasks=[task],
        iterations=[],
    )
    service.plans["plan-1"] = plan
    
    agents = [
        make_agent("new-coder-id", "Coder Agent", AgentType.CODER),
    ]
    
    with patch.object(service, "_save_plans") as mock_save, patch.object(
        coordinator_module.agent_manager, "get_all_agents", return_value=agents
    ):
        service._reassign_agents("plan-1")
    
    assert plan.tasks[0].assigned_agent_id == "new-coder-id"
    mock_save.assert_called_once()


@patch.object(CoordinatorService, "_load_plans", return_value=None)
def test_reassign_agents_handles_iteration_tasks(_mock_load_plans):
    """Iteration tasks should be reassigned when agent IDs change."""
    service = CoordinatorService()
    
    iteration_task = IterationTask(
        id="iter-task-1",
        iteration_round=1,
        title="Iteration Task",
        assigned_agent_id="old-coder-id",
        assigned_agent_type="coder",
        status=TaskStatus.PENDING,
    )
    
    iteration = IterationRound(
        round_number=1,
        iteration_request="fix bugs",
        tasks=[iteration_task],
    )
    
    plan = Plan(
        id="plan-1",
        title="Test Plan",
        original_request="test",
        tasks=[],
        iterations=[iteration],
    )
    service.plans["plan-1"] = plan
    
    agents = [
        make_agent("new-coder-id", "Coder Agent", AgentType.CODER),
    ]
    
    with patch.object(service, "_save_plans") as mock_save, patch.object(
        coordinator_module.agent_manager, "get_all_agents", return_value=agents
    ):
        service._reassign_agents("plan-1")
    
    assert plan.iterations[0].tasks[0].assigned_agent_id == "new-coder-id"
    mock_save.assert_called_once()


@patch.object(CoordinatorService, "_load_plans", return_value=None)
def test_reassign_agents_handles_both_main_and_iteration_tasks(_mock_load_plans):
    """Both main tasks and iteration tasks should be reassigned."""
    service = CoordinatorService()
    
    main_task = PlanTask(
        id="main-task-1",
        title="Main Task",
        assigned_agent_id="old-coder-id",
        assigned_agent_type="coder",
        status=TaskStatus.PENDING,
    )
    
    iteration_task = IterationTask(
        id="iter-task-1",
        iteration_round=1,
        title="Iteration Task",
        assigned_agent_id="old-tester-id",
        assigned_agent_type="tester",
        status=TaskStatus.PENDING,
    )
    
    iteration = IterationRound(
        round_number=1,
        iteration_request="add tests",
        tasks=[iteration_task],
    )
    
    plan = Plan(
        id="plan-1",
        title="Test Plan",
        original_request="test",
        tasks=[main_task],
        iterations=[iteration],
    )
    service.plans["plan-1"] = plan
    
    agents = [
        make_agent("new-coder-id", "Coder Agent", AgentType.CODER),
        make_agent("new-tester-id", "Tester Agent", AgentType.TESTER),
    ]
    
    with patch.object(service, "_save_plans") as mock_save, patch.object(
        coordinator_module.agent_manager, "get_all_agents", return_value=agents
    ):
        service._reassign_agents("plan-1")
    
    assert plan.tasks[0].assigned_agent_id == "new-coder-id"
    assert plan.iterations[0].tasks[0].assigned_agent_id == "new-tester-id"
    mock_save.assert_called_once()


@patch.object(CoordinatorService, "_load_plans", return_value=None)
def test_reassign_agents_respects_selected_agent_order(_mock_load_plans):
    """Selected agent IDs order should be respected during reassignment."""
    service = CoordinatorService()
    
    task = PlanTask(
        id="task-1",
        title="Test Task",
        assigned_agent_id="old-coder-id",
        assigned_agent_type="coder",
        status=TaskStatus.PENDING,
    )
    
    plan = Plan(
        id="plan-1",
        title="Test Plan",
        original_request="test",
        tasks=[task],
        selected_agent_ids=["coder-b", "coder-a"],  # Order matters
        iterations=[],
    )
    service.plans["plan-1"] = plan
    
    agents = [
        make_agent("coder-a", "Coder A", AgentType.CODER),
        make_agent("coder-b", "Coder B", AgentType.CODER),
    ]
    
    with patch.object(service, "_save_plans") as mock_save, patch.object(
        coordinator_module.agent_manager, "get_all_agents", return_value=agents
    ):
        service._reassign_agents("plan-1")
    
    # Should use first agent in selected order (coder-b)
    assert plan.tasks[0].assigned_agent_id == "coder-b"
    mock_save.assert_called_once()


@patch.object(CoordinatorService, "_load_plans", return_value=None)
def test_reassign_agents_falls_back_when_selected_ids_are_stale(_mock_load_plans):
    """When selected_agent_ids are stale, should fall back to all available agents."""
    service = CoordinatorService()
    
    main_task = PlanTask(
        id="main-task-1",
        title="Main Task",
        assigned_agent_id="old-coder-id",
        assigned_agent_type="coder",
        status=TaskStatus.PENDING,
    )
    
    iteration_task = IterationTask(
        id="iter-task-1",
        iteration_round=1,
        title="Iteration Task",
        assigned_agent_id="old-tester-id",
        assigned_agent_type="tester",
        status=TaskStatus.PENDING,
    )
    
    iteration = IterationRound(
        round_number=1,
        iteration_request="fix",
        tasks=[iteration_task],
    )
    
    plan = Plan(
        id="plan-1",
        title="Test Plan",
        original_request="test",
        tasks=[main_task],
        selected_agent_ids=["stale-coder", "stale-tester"],  # These don't exist anymore
        iterations=[iteration],
    )
    service.plans["plan-1"] = plan
    
    # Only return new agents (old selected IDs are stale)
    agents = [
        make_agent("new-coder-id", "Coder", AgentType.CODER),
        make_agent("new-tester-id", "Tester", AgentType.TESTER),
    ]
    
    with patch.object(service, "_save_plans") as mock_save, patch.object(
        coordinator_module.agent_manager, "get_all_agents", return_value=agents
    ):
        service._reassign_agents("plan-1")
    
    assert plan.tasks[0].assigned_agent_id == "new-coder-id"
    assert plan.iterations[0].tasks[0].assigned_agent_id == "new-tester-id"
    mock_save.assert_called_once()


@patch.object(CoordinatorService, "_load_plans", return_value=None)
def test_reassign_agents_skips_tasks_without_available_agent_type(_mock_load_plans):
    """Tasks with no available agent of their type should be skipped."""
    service = CoordinatorService()
    
    task_with_agent = PlanTask(
        id="task-1",
        title="Task with Agent",
        assigned_agent_id="old-coder-id",
        assigned_agent_type="coder",
        status=TaskStatus.PENDING,
    )
    
    task_without_agent = PlanTask(
        id="task-2",
        title="Task without Agent",
        assigned_agent_id="old-legacy-id",
        assigned_agent_type="legacy",  # No legacy agent available
        status=TaskStatus.PENDING,
    )
    
    iteration_task = IterationTask(
        id="iter-task-1",
        iteration_round=1,
        title="Iteration Task",
        assigned_agent_id="old-legacy-id",
        assigned_agent_type="legacy",  # No legacy agent available
        status=TaskStatus.PENDING,
    )
    
    iteration = IterationRound(
        round_number=1,
        iteration_request="fix",
        tasks=[iteration_task],
    )
    
    plan = Plan(
        id="plan-1",
        title="Test Plan",
        original_request="test",
        tasks=[task_with_agent, task_without_agent],
        iterations=[iteration],
    )
    service.plans["plan-1"] = plan
    
    agents = [
        make_agent("new-coder-id", "Coder", AgentType.CODER),
    ]
    
    with patch.object(service, "_save_plans") as mock_save, patch.object(
        coordinator_module.agent_manager, "get_all_agents", return_value=agents
    ):
        service._reassign_agents("plan-1")
    
    # Task with available agent type should be reassigned
    assert plan.tasks[0].assigned_agent_id == "new-coder-id"
    # Tasks without available agent type should keep old assignment
    assert plan.tasks[1].assigned_agent_id == "old-legacy-id"
    assert plan.iterations[0].tasks[0].assigned_agent_id == "old-legacy-id"
    # Should still save since at least one task was reassigned
    mock_save.assert_called_once()


@patch.object(CoordinatorService, "_load_plans", return_value=None)
def test_reassign_agents_handles_multiple_iterations(_mock_load_plans):
    """Tasks across multiple iteration rounds should all be reassigned."""
    service = CoordinatorService()
    
    iteration_1_task = IterationTask(
        id="iter-1-task-1",
        iteration_round=1,
        title="Iteration 1 Task",
        assigned_agent_id="old-coder-id",
        assigned_agent_type="coder",
        status=TaskStatus.PENDING,
    )
    
    iteration_1 = IterationRound(
        round_number=1,
        iteration_request="fix bugs",
        tasks=[iteration_1_task],
    )
    
    iteration_2_task = IterationTask(
        id="iter-2-task-1",
        iteration_round=2,
        title="Iteration 2 Task",
        assigned_agent_id="old-tester-id",
        assigned_agent_type="tester",
        status=TaskStatus.PENDING,
    )
    
    iteration_2 = IterationRound(
        round_number=2,
        iteration_request="add tests",
        tasks=[iteration_2_task],
    )
    
    plan = Plan(
        id="plan-1",
        title="Test Plan",
        original_request="test",
        tasks=[],
        iterations=[iteration_1, iteration_2],
    )
    service.plans["plan-1"] = plan
    
    agents = [
        make_agent("new-coder-id", "Coder", AgentType.CODER),
        make_agent("new-tester-id", "Tester", AgentType.TESTER),
    ]
    
    with patch.object(service, "_save_plans") as mock_save, patch.object(
        coordinator_module.agent_manager, "get_all_agents", return_value=agents
    ):
        service._reassign_agents("plan-1")
    
    assert plan.iterations[0].tasks[0].assigned_agent_id == "new-coder-id"
    assert plan.iterations[1].tasks[0].assigned_agent_id == "new-tester-id"
    mock_save.assert_called_once()


@patch.object(CoordinatorService, "_load_plans", return_value=None)
def test_reassign_agents_no_save_when_no_changes(_mock_load_plans):
    """Should not save plans when no reassignments are needed."""
    service = CoordinatorService()
    
    task = PlanTask(
        id="task-1",
        title="Test Task",
        assigned_agent_id="current-coder-id",
        assigned_agent_type="coder",
        status=TaskStatus.PENDING,
    )
    
    plan = Plan(
        id="plan-1",
        title="Test Plan",
        original_request="test",
        tasks=[task],
        iterations=[],
    )
    service.plans["plan-1"] = plan
    
    agents = [
        make_agent("current-coder-id", "Coder", AgentType.CODER),
    ]
    
    with patch.object(service, "_save_plans") as mock_save, patch.object(
        coordinator_module.agent_manager, "get_all_agents", return_value=agents
    ):
        service._reassign_agents("plan-1")
    
    # Agent ID didn't change, so no save needed
    mock_save.assert_not_called()


@patch.object(CoordinatorService, "_load_plans", return_value=None)
def test_reassign_agents_handles_empty_iterations(_mock_load_plans):
    """Should handle plans with no iterations gracefully."""
    service = CoordinatorService()
    
    task = PlanTask(
        id="task-1",
        title="Test Task",
        assigned_agent_id="old-coder-id",
        assigned_agent_type="coder",
        status=TaskStatus.PENDING,
    )
    
    plan = Plan(
        id="plan-1",
        title="Test Plan",
        original_request="test",
        tasks=[task],
        iterations=[],  # No iterations
    )
    service.plans["plan-1"] = plan
    
    agents = [
        make_agent("new-coder-id", "Coder", AgentType.CODER),
    ]
    
    with patch.object(service, "_save_plans") as mock_save, patch.object(
        coordinator_module.agent_manager, "get_all_agents", return_value=agents
    ):
        service._reassign_agents("plan-1")
    
    assert plan.tasks[0].assigned_agent_id == "new-coder-id"
    mock_save.assert_called_once()


@patch.object(CoordinatorService, "_load_plans", return_value=None)
def test_reassign_agents_handles_nonexistent_plan(_mock_load_plans):
    """Should handle nonexistent plan ID gracefully."""
    service = CoordinatorService()
    
    # No plan added to service.plans
    
    with patch.object(service, "_save_plans") as mock_save:
        service._reassign_agents("nonexistent-plan-id")
    
    # Should not crash or save
    mock_save.assert_not_called()
