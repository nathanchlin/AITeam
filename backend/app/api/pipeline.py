from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from typing import List
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
async def start_pipeline(request: PipelineRequest):
    """Start a new pipeline: Discussion → Planning → Execution"""
    import asyncio
    from app.main import websocket_manager

    coordinator.set_websocket_manager(websocket_manager)

    # Create plan first
    plan = await coordinator.create_plan(
        request=request.request,
        target_output=request.target_output,
        selected_agent_ids=request.selected_agent_ids,
    )

    # Run pipeline in background
    async def run_pipeline_safe():
        try:
            await coordinator.run_pipeline_with_plan(plan.id)
        except Exception as e:
            print(f"[Pipeline Error] {e}")
            import traceback
            traceback.print_exc()

    asyncio.create_task(run_pipeline_safe())

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
    output_dir = output_manager.get_output_path(plan_id)
    filepath = os.path.join(output_dir, filename)

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
async def recover_stuck_pipeline(plan_id: str):
    """Recover a stuck pipeline by restarting it"""
    plan = coordinator.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    if plan.status != PlanStatus.EXECUTING:
        raise HTTPException(status_code=400, detail="Plan is not in executing state")

    # Reset all running tasks to pending
    for task in plan.tasks:
        if task.status == TaskStatus.RUNNING:
            task.status = TaskStatus.PENDING

    # Restart execution
    import asyncio
    asyncio.create_task(coordinator.execute_plan(plan_id))

    return {"message": "Pipeline recovery started", "plan_id": plan_id}


@router.post("/resume/{plan_id}")
async def resume_pipeline(plan_id: str):
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

    # Check which phase to resume from
    if plan.status == PlanStatus.DRAFT:
        # Resume from beginning
        import asyncio
        asyncio.create_task(coordinator.run_pipeline_with_plan(plan_id))
        return {"message": "Pipeline resumed from beginning", "plan_id": plan_id, "phase": "draft"}

    elif plan.status == PlanStatus.DISCUSSING:
        # Resume from discussion phase
        import asyncio
        async def resume_from_discussion():
            await coordinator.organize_discussion(plan_id)
            await coordinator.generate_plan(plan_id)
            await coordinator.execute_plan(plan_id)
        asyncio.create_task(resume_from_discussion())
        return {"message": "Pipeline resumed from discussion", "plan_id": plan_id, "phase": "discussing"}

    elif plan.status == PlanStatus.APPROVED:
        # Resume from execution phase
        import asyncio
        asyncio.create_task(coordinator.execute_plan(plan_id))
        return {"message": "Pipeline resumed from execution", "plan_id": plan_id, "phase": "approved"}

    elif plan.status == PlanStatus.EXECUTING:
        # Resume execution (reset running tasks to pending)
        for task in plan.tasks:
            if task.status == TaskStatus.RUNNING:
                task.status = TaskStatus.PENDING
        import asyncio
        asyncio.create_task(coordinator.execute_plan(plan_id))
        return {"message": "Pipeline resumed from execution", "plan_id": plan_id, "phase": "executing"}

    elif plan.status == PlanStatus.COMPLETED:
        return {"message": "Pipeline already completed", "plan_id": plan_id, "phase": "completed"}

    else:
        raise HTTPException(status_code=400, detail=f"Unknown plan status: {plan.status}")
