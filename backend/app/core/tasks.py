"""
Celery tasks for pipeline execution with persistence.
"""

import asyncio
import json
from typing import Dict, Any, Optional
from celery import shared_task, current_task
from celery.result import AsyncResult

from app.core.celery_app import celery_app
from app.core.broadcast import broadcast_manager
from app.config import settings


def run_async(coro):
    """Run async coroutine in sync context for Celery tasks."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(
    bind=True,
    name="app.core.tasks.run_pipeline_task",
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
)
def run_pipeline_task(self, plan_id: str) -> Dict[str, Any]:
    """
    Execute a complete pipeline for a plan.

    Args:
        plan_id: The UUID of the plan to execute

    Returns:
        Dict with execution results
    """
    from app.services.coordinator import coordinator

    # Set up broadcast manager for cross-process communication
    coordinator.set_broadcast_manager(broadcast_manager)

    # Update task status
    self.update_state(
        state="PROGRESS",
        meta={"plan_id": plan_id, "phase": "starting", "progress": 0}
    )

    try:
        # Run the async pipeline in sync context
        result = run_async(_run_pipeline_async(plan_id, self))

        return {
            "status": "completed",
            "plan_id": plan_id,
            "result": result,
        }

    except Exception as e:
        import traceback
        traceback.print_exc()

        # Broadcast error
        run_async(broadcast_manager.broadcast({
            "type": "pipeline_error",
            "data": {
                "plan_id": plan_id,
                "error": str(e),
                "traceback": traceback.format_exc(),
            }
        }))

        # Retry logic
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e)

        return {
            "status": "failed",
            "plan_id": plan_id,
            "error": str(e),
        }


async def _run_pipeline_async(plan_id: str, task) -> str:
    """Async implementation of pipeline execution."""
    from app.services.coordinator import coordinator

    # Phase 1: Analyze request
    task.update_state(
        state="PROGRESS",
        meta={"plan_id": plan_id, "phase": "analyzing", "progress": 10}
    )

    await coordinator.analyze_request(plan_id)

    # Phase 2: Organize discussion
    task.update_state(
        state="PROGRESS",
        meta={"plan_id": plan_id, "phase": "discussing", "progress": 30}
    )

    await coordinator.organize_discussion(plan_id)

    # Phase 3: Generate plan
    task.update_state(
        state="PROGRESS",
        meta={"plan_id": plan_id, "phase": "planning", "progress": 50}
    )

    await coordinator.generate_plan(plan_id)

    # Phase 4: Execute plan
    task.update_state(
        state="PROGRESS",
        meta={"plan_id": plan_id, "phase": "executing", "progress": 70}
    )

    result = await coordinator.execute_plan(plan_id)

    task.update_state(
        state="PROGRESS",
        meta={"plan_id": plan_id, "phase": "completed", "progress": 100}
    )

    return result


@celery_app.task(
    bind=True,
    name="app.core.tasks.execute_phase_task",
    max_retries=2,
    default_retry_delay=30,
)
def execute_phase_task(self, plan_id: str, phase: str, from_task_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Execute a specific phase of the pipeline (for recovery).

    Args:
        plan_id: The UUID of the plan
        phase: The phase to execute ('analyze', 'discuss', 'plan', 'execute')
        from_task_id: Optional task ID to resume from

    Returns:
        Dict with execution results
    """
    from app.services.coordinator import coordinator

    coordinator.set_broadcast_manager(broadcast_manager)

    # Re-assign agents after worker restart
    coordinator._reassign_agents(plan_id)

    try:
        if phase == "analyze":
            result = run_async(coordinator.analyze_request(plan_id))

        elif phase == "discuss":
            result = run_async(coordinator.organize_discussion(plan_id))

        elif phase == "plan":
            plan = run_async(coordinator.generate_plan(plan_id))
            result = plan.model_dump()

        elif phase == "execute":
            result = run_async(coordinator.execute_plan(plan_id))

        elif phase == "full":
            # Run from current state
            result = run_async(coordinator.run_pipeline_with_plan(plan_id))

        else:
            raise ValueError(f"Unknown phase: {phase}")

        return {
            "status": "completed",
            "plan_id": plan_id,
            "phase": phase,
            "result": result,
        }

    except Exception as e:
        import traceback
        traceback.print_exc()

        if self.request.retries < self.max_retries:
            raise self.retry(exc=e)

        return {
            "status": "failed",
            "plan_id": plan_id,
            "phase": phase,
            "error": str(e),
        }


@celery_app.task(name="app.core.tasks.health_check")
def health_check() -> Dict[str, Any]:
    """
    Health check task for monitoring.

    Returns:
        Dict with health status
    """
    from app.services.coordinator import coordinator
    from app.services.agent_manager import agent_manager
    import redis
    import time

    result = {
        "timestamp": time.time(),
        "status": "healthy",
        "checks": {},
    }

    # Check Redis connection
    try:
        r = redis.from_url(settings.redis_url)
        r.ping()
        result["checks"]["redis"] = "ok"
    except Exception as e:
        result["checks"]["redis"] = f"failed: {str(e)}"
        result["status"] = "degraded"

    # Check plans count
    try:
        result["checks"]["plans_count"] = len(coordinator.plans)
    except Exception as e:
        result["checks"]["plans_count"] = f"error: {str(e)}"

    # Check agents count
    try:
        result["checks"]["agents_count"] = len(agent_manager.get_all_agents())
    except Exception as e:
        result["checks"]["agents_count"] = f"error: {str(e)}"

    return result


def get_task_status(task_id: str) -> Dict[str, Any]:
    """
    Get the status of a Celery task.

    Args:
        task_id: The Celery task ID

    Returns:
        Dict with task status and result
    """
    result = AsyncResult(task_id, app=celery_app)

    response = {
        "task_id": task_id,
        "status": result.status,
        "ready": result.ready(),
        "successful": result.successful() if result.ready() else None,
        "failed": result.failed() if result.ready() else None,
    }

    if result.ready():
        if result.successful():
            response["result"] = result.result
        else:
            response["error"] = str(result.result)
    else:
        # Get progress info if available
        info = result.info
        if isinstance(info, dict):
            response["progress"] = info

    return response


def recover_incomplete_plans() -> Dict[str, Any]:
    """
    Scan for incomplete plans and submit recovery tasks.

    This should be called on application startup.

    Returns:
        Dict with recovery results
    """
    from app.services.coordinator import coordinator
    from app.models.schemas import PlanStatus

    recovered = []
    skipped = []

    for plan_id, plan in coordinator.plans.items():
        # Skip completed plans
        if plan.status == PlanStatus.COMPLETED:
            continue

        # Determine which phase to recover from
        if plan.status == PlanStatus.DRAFT:
            phase = "full"
        elif plan.status == PlanStatus.DISCUSSING:
            phase = "discuss"
        elif plan.status == PlanStatus.APPROVED:
            phase = "execute"
        elif plan.status == PlanStatus.EXECUTING:
            phase = "execute"
        else:
            skipped.append({
                "plan_id": plan_id,
                "reason": f"Unknown status: {plan.status}",
            })
            continue

        # Submit recovery task
        task = execute_phase_task.delay(plan_id, phase)
        recovered.append({
            "plan_id": plan_id,
            "phase": phase,
            "celery_task_id": task.id,
        })

    return {
        "recovered": recovered,
        "skipped": skipped,
        "total_checked": len(coordinator.plans),
    }
