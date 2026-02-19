from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from typing import List, Optional
import os
from app.models.schemas import (
    PipelineRequest,
    Plan, PlanCreate, PlanUpdate,
    DiscussionMessage, DiscussionMessageCreate,
    PlanStatus, TaskStatus,
)
from app.services.coordinator import coordinator
from app.services.output_manager import output_manager
from app.services.agent_manager import agent_manager

router = APIRouter(prefix="/pipeline", tags=["pipeline"])


@router.post("/start")
async def start_pipeline(request: PipelineRequest, background_tasks: BackgroundTasks):
    """Start a new pipeline: Discussion → Planning → Execution"""
    from app.main import websocket_manager

    coordinator.set_websocket_manager(websocket_manager)

    # Create plan first
    plan = await coordinator.create_plan(
        request=request.request,
        target_output=request.target_output,
        selected_agent_ids=request.selected_agent_ids,
    )

    # Run pipeline in background (replaces Celery task execution)
    async def run_pipeline_background():
        try:
            await coordinator.analyze_request(plan.id)
            await coordinator.organize_discussion(plan.id)
            await coordinator.generate_plan(plan.id)
            await coordinator.execute_plan(plan.id)
        except Exception as e:
            print(f"[Pipeline] Error executing pipeline {plan.id}: {e}")
            import traceback
            traceback.print_exc()

    background_tasks.add_task(run_pipeline_background)

    return {
        "message": "Pipeline started",
        "plan_id": plan.id,
        "request": request.request,
        "target_output": request.target_output,
        "selected_agent_ids": request.selected_agent_ids,
    }


@router.post("/create", response_model=dict)
async def create_plan(plan_data: PlanCreate):
    """Create a new plan (without starting execution)"""
    plan = await coordinator.create_plan(
        request=plan_data.original_request,
        target_output=plan_data.target_output or "web-app",
    )
    return plan.model_dump()


@router.get("/plans", response_model=List[dict])
async def list_plans():
    """List all plans"""
    plans = coordinator.get_all_plans()
    return [p.model_dump() for p in plans]


@router.get("/plans/{plan_id}", response_model=dict)
async def get_plan(plan_id: str):
    """Get plan by ID"""
    plan = coordinator.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan.model_dump()


@router.delete("/plans/{plan_id}")
async def delete_plan(plan_id: str):
    """Delete a plan"""
    if not coordinator.delete_plan(plan_id):
        raise HTTPException(status_code=404, detail="Plan not found")
    return {"message": "Plan deleted successfully", "plan_id": plan_id}


@router.post("/plans/{plan_id}/analyze")
async def analyze_request(plan_id: str):
    """Phase 1: Analyze the request"""
    from app.main import websocket_manager
    coordinator.set_websocket_manager(websocket_manager)

    result = await coordinator.analyze_request(plan_id)
    return {"message": "Analysis completed", "result": result}


@router.post("/plans/{plan_id}/discuss")
async def organize_discussion(plan_id: str):
    """Phase 2: Organize discussion between agents"""
    from app.main import websocket_manager
    coordinator.set_websocket_manager(websocket_manager)

    result = await coordinator.organize_discussion(plan_id)
    return {"message": "Discussion completed", "result": result}


@router.post("/plans/{plan_id}/generate")
async def generate_plan(plan_id: str):
    """Phase 3: Generate execution plan"""
    from app.main import websocket_manager
    coordinator.set_websocket_manager(websocket_manager)

    plan = await coordinator.generate_plan(plan_id)
    return plan.model_dump()


@router.post("/plans/{plan_id}/execute")
async def execute_plan(plan_id: str):
    """Phase 4: Execute the plan"""
    from app.main import websocket_manager
    coordinator.set_websocket_manager(websocket_manager)

    result = await coordinator.execute_plan(plan_id)
    return {"message": "Execution completed", "result": result}


@router.post("/plans/{plan_id}/discussion", response_model=dict)
async def add_discussion_message(plan_id: str, msg_data: DiscussionMessageCreate):
    """Add a message to plan discussion"""
    plan = coordinator.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    # For now, use assistant as the sender (in real app, would be from user)
    agents = agent_manager.get_all_agents()
    assistant = next((a for a in agents if a.type == "assistant"), None)

    if not assistant:
        raise HTTPException(status_code=400, detail="No assistant agent found")

    msg = await coordinator.add_discussion_message(
        plan_id=plan_id,
        agent_id=assistant.id,
        agent_name=assistant.name,
        agent_type="assistant",
        content=msg_data.content,
        message_type=msg_data.message_type,
        reply_to=msg_data.reply_to,
    )
    return msg.model_dump()


@router.get("/output/{plan_id}")
async def get_output(plan_id: str):
    """Get output files for a plan"""
    output_dir = output_manager.get_output_path(plan_id)
    if not os.path.exists(output_dir):
        raise HTTPException(status_code=404, detail="Output not found")

    # List all files
    files = []
    for f in os.listdir(output_dir):
        filepath = os.path.join(output_dir, f)
        files.append({
            "name": f,
            "size": os.path.getsize(filepath),
            "modified": os.path.getmtime(filepath),
        })

    return {"plan_id": plan_id, "output_dir": output_dir, "files": files}


@router.get("/output/{plan_id}/files/{filename}")
async def get_output_file(plan_id: str, filename: str):
    """Get a specific output file"""
    try:
        output_dir = output_manager.get_output_path(plan_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Output path error: {str(e)}")
    filepath = os.path.join(output_dir, filename)

    # 若请求的是 index.html 但不存在，尝试按需合并生成（流水线可能未跑完或未生成 index.html）
    if filename == "index.html" and not os.path.exists(filepath):
        plan = coordinator.get_plan(plan_id)
        plan_title = plan.title if plan else "Output"
        try:
            if output_manager.consolidate_web_app(plan_id, plan_title):
                filepath = os.path.join(output_dir, filename)
                if os.path.exists(filepath):
                    return FileResponse(filepath)
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate index.html: {str(e)}",
            )
        raise HTTPException(status_code=404, detail="index.html not found and could not be generated from fragments")

    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(filepath)


@router.get("/output/{plan_id}/preview")
async def get_output_preview(plan_id: str):
    """Get preview URL for the generated output"""
    output_dir = output_manager.get_output_path(plan_id)

    # Check for index.html
    index_path = os.path.join(output_dir, "index.html")
    if os.path.exists(index_path):
        return {
            "preview_url": f"/api/pipeline/output/{plan_id}/files/index.html",
            "has_preview": True
        }

    return {"has_preview": False, "message": "No preview available"}


@router.get("/health")
async def check_pipeline_health():
    """Check for stuck pipelines and return status"""
    stuck_pipelines = []
    running_pipelines = []
    TASK_TIMEOUT_SECONDS = 900  # 15 minutes

    for plan_id, plan in coordinator.plans.items():
        if plan.status == PlanStatus.EXECUTING:
            # Check if any task has been running for too long
            import time
            current_time = time.time()

            for task in plan.tasks:
                if task.status == TaskStatus.RUNNING:
                    running_pipelines.append({
                        "plan_id": plan_id,
                        "plan_title": plan.title,
                        "running_task": task.title,
                    })

                    # Check if task is stuck (running for more than timeout + buffer)
                    # Note: This is a safety check; actual timeout is handled in coordinator
                    if plan.started_at:
                        elapsed = current_time - plan.started_at.timestamp()
                        if elapsed > TASK_TIMEOUT_SECONDS * 4:  # 4x timeout = definitely stuck
                            stuck_pipelines.append({
                                "plan_id": plan_id,
                                "plan_title": plan.title,
                                "running_task": task.title,
                                "elapsed_seconds": int(elapsed),
                                "message": "Pipeline may be stuck (running for over 1 hour)",
                            })

    return {
        "running_pipelines": running_pipelines,
        "stuck_pipelines": stuck_pipelines,
        "total_plans": len(coordinator.plans),
        "task_timeout_seconds": TASK_TIMEOUT_SECONDS,
        "max_retries_per_task": 3,
    }


@router.post("/recover/{plan_id}")
async def recover_stuck_pipeline(plan_id: str, background_tasks: BackgroundTasks):
    """Recover a stuck pipeline by restarting execution"""
    from app.main import websocket_manager

    coordinator.set_websocket_manager(websocket_manager)

    plan = coordinator.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    if plan.status != PlanStatus.EXECUTING:
        raise HTTPException(status_code=400, detail="Plan is not in executing state")

    # Reset all running tasks to pending
    for task in plan.tasks:
        if task.status == TaskStatus.RUNNING:
            task.status = TaskStatus.PENDING

    # Run execution in background
    async def run_execute_background():
        try:
            await coordinator.execute_plan(plan_id)
        except Exception as e:
            print(f"[Pipeline] Error recovering pipeline {plan_id}: {e}")

    background_tasks.add_task(run_execute_background)

    return {
        "message": "Pipeline recovery started",
        "plan_id": plan_id,
    }


@router.post("/resume/{plan_id}")
async def resume_pipeline(plan_id: str, background_tasks: BackgroundTasks):
    """Resume an interrupted pipeline from its current state"""
    from app.main import websocket_manager

    coordinator.set_websocket_manager(websocket_manager)

    plan = coordinator.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    # Re-assign agents to tasks (agent IDs may have changed after restart)
    coordinator._reassign_agents(plan_id)

    # Check if there are pending tasks even though status is completed
    pending_tasks = [t for t in plan.tasks if t.status == TaskStatus.PENDING]
    if plan.status == PlanStatus.COMPLETED and pending_tasks:
        # Reset status to executing if there are pending tasks
        plan.status = PlanStatus.EXECUTING

    async def run_full_pipeline():
        try:
            await coordinator.analyze_request(plan_id)
            await coordinator.organize_discussion(plan_id)
            await coordinator.generate_plan(plan_id)
            await coordinator.execute_plan(plan_id)
        except Exception as e:
            print(f"[Pipeline] Error in resumed pipeline {plan_id}: {e}")

    async def run_execute_only():
        try:
            await coordinator.execute_plan(plan_id)
        except Exception as e:
            print(f"[Pipeline] Error executing pipeline {plan_id}: {e}")

    # Check which phase to resume from
    if plan.status == PlanStatus.DRAFT:
        background_tasks.add_task(run_full_pipeline)
        return {
            "message": "Pipeline resumed from beginning",
            "plan_id": plan_id,
            "phase": "draft",
        }

    elif plan.status == PlanStatus.DISCUSSING:
        background_tasks.add_task(run_full_pipeline)
        return {
            "message": "Pipeline resumed from discussion",
            "plan_id": plan_id,
            "phase": "discussing",
        }

    elif plan.status == PlanStatus.APPROVED:
        background_tasks.add_task(run_execute_only)
        return {
            "message": "Pipeline resumed from execution",
            "plan_id": plan_id,
            "phase": "approved",
        }

    elif plan.status == PlanStatus.EXECUTING:
        # Resume execution (reset running tasks to pending)
        for task in plan.tasks:
            if task.status == TaskStatus.RUNNING:
                task.status = TaskStatus.PENDING
        background_tasks.add_task(run_execute_only)
        return {
            "message": "Pipeline resumed from execution",
            "plan_id": plan_id,
            "phase": "executing",
        }

    elif plan.status == PlanStatus.COMPLETED:
        return {"message": "Pipeline already completed", "plan_id": plan_id, "phase": "completed"}

    else:
        raise HTTPException(status_code=400, detail=f"Unknown plan status: {plan.status}")


@router.post("/restart/{plan_id}")
async def restart_pipeline(plan_id: str, background_tasks: BackgroundTasks):
    """Restart a plan from the beginning: clear tasks and discussion, then run full pipeline"""
    from app.main import websocket_manager

    coordinator.set_websocket_manager(websocket_manager)

    plan = coordinator.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    # Reset to initial state (keep original_request, target_output, selected_agent_ids)
    plan.status = PlanStatus.DRAFT
    plan.tasks = []
    plan.discussion = []
    plan.started_at = None
    plan.completed_at = None
    coordinator._save_plans()

    # Run pipeline in background
    async def run_pipeline_background():
        try:
            await coordinator.analyze_request(plan_id)
            await coordinator.organize_discussion(plan_id)
            await coordinator.generate_plan(plan_id)
            await coordinator.execute_plan(plan_id)
        except Exception as e:
            print(f"[Pipeline] Error in restarted pipeline {plan_id}: {e}")

    background_tasks.add_task(run_pipeline_background)

    return {
        "message": "Plan restarted from beginning",
        "plan_id": plan_id,
    }


@router.get("/task/{task_id}")
async def get_task_status_endpoint(task_id: str):
    """Get the status of a task (deprecated - Celery no longer used)"""
    return {
        "task_id": task_id,
        "status": "deprecated",
        "message": "Celery tasks are no longer used. Use /plans/{plan_id} to check pipeline status."
    }
