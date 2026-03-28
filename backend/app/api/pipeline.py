from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from typing import List, Optional
import os
import shutil
from app.models.schemas import (
    PipelineRequest,
    IterationRequest,
    Plan, PlanCreate, PlanUpdate,
    DiscussionMessage, DiscussionMessageCreate,
    PlanStatus, TaskStatus,
    ArchiveDiffRequest,
    CreateArchiveRequest,
)
from app.services.coordinator import coordinator
from app.services.output_manager import output_manager
from app.services.agent_manager import agent_manager
from app.services.pipeline_queue import pipeline_queue

router = APIRouter(prefix="/pipeline", tags=["pipeline"])


@router.post("/start")
async def start_pipeline(request: PipelineRequest, background_tasks: BackgroundTasks):
    """Start a new pipeline: Discussion → Planning → Execution

    Uses queue mechanism to limit concurrent pipelines to 5.
    If at capacity, the pipeline will be queued and started when a slot is available.
    """
    from app.main import websocket_manager

    coordinator.set_websocket_manager(websocket_manager)
    pipeline_queue.set_websocket_manager(websocket_manager)
    pipeline_queue.set_coordinator(coordinator)

    # Create plan first
    plan = await coordinator.create_plan(
        request=request.request,
        target_output=request.target_output,
        selected_agent_ids=request.selected_agent_ids,
    )

    # Persist skip_discussion on plan for resume/restart
    plan.skip_discussion = request.skip_discussion

    # Add to queue (will start immediately if under limit, otherwise queued)
    queue_result = await pipeline_queue.enqueue(
        plan_id=plan.id,
        request=request.request,
        target_output=request.target_output,
        selected_agent_ids=request.selected_agent_ids,
        skip_discussion=request.skip_discussion,
    )

    return {
        "message": "Pipeline queued" if queue_result["status"] == "queued" else "Pipeline started",
        "plan_id": plan.id,
        "request": request.request,
        "target_output": request.target_output,
        "selected_agent_ids": request.selected_agent_ids,
        "queue_status": queue_result,
    }


@router.post("/create", response_model=dict)
async def create_plan(plan_data: PlanCreate):
    """Create a new plan (without starting execution)"""
    plan = await coordinator.create_plan(
        request=plan_data.original_request,
        target_output=plan_data.target_output or "web-app",
    )
    return plan.model_dump()


@router.get("/queue/status")
async def get_queue_status():
    """Get Pipeline queue status

    Returns:
        - running_count: Number of currently running pipelines
        - max_concurrent: Maximum allowed concurrent pipelines (5)
        - queue_length: Number of pipelines waiting in queue
        - running_pipelines: List of running pipeline details
        - queued_pipelines: List of queued pipeline details
    """
    return pipeline_queue.get_queue_status()


@router.get("/queue/position/{plan_id}")
async def get_plan_queue_position(plan_id: str):
    """Get queue position for a specific plan

    Returns:
        - status: "running", "queued", or null if not found
        - position: 0 for running, 1+ for queue position
    """
    position = pipeline_queue.get_plan_queue_position(plan_id)
    if position is None:
        raise HTTPException(status_code=404, detail="Plan not found in queue or running")
    return {
        "plan_id": plan_id,
        **position
    }


@router.delete("/queue/cancel/{plan_id}")
async def cancel_queued_pipeline(plan_id: str):
    """Cancel a pipeline from the queue

    Note: Cannot cancel a pipeline that is already running
    """
    cancelled = await pipeline_queue.cancel_pipeline(plan_id)
    if not cancelled:
        raise HTTPException(
            status_code=400,
            detail="Cannot cancel: pipeline is running or not found in queue"
        )
    return {
        "message": "Pipeline cancelled from queue",
        "plan_id": plan_id
    }


@router.delete("/queue/clear")
async def clear_queue():
    """Clear all pipelines from the queue (not running ones)"""
    count = await pipeline_queue.clear_queue()
    return {
        "message": f"Cleared {count} pipelines from queue",
        "cleared_count": count
    }


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


@router.post("/plans/{plan_id}/complete")
async def complete_plan(plan_id: str):
    """Mark a plan as completed and broadcast update"""
    from app.main import websocket_manager

    plan = coordinator.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    # Update plan status
    from datetime import datetime
    plan.status = "completed"
    plan.completed_at = datetime.utcnow()
    coordinator._save_plans()

    # Broadcast update to WebSocket clients
    if websocket_manager:
        await websocket_manager.broadcast({
            "type": "plan_update",
            "data": {
                "plan_id": plan_id,
                "status": "completed",
                "plan": plan.model_dump(),
            }
        })

    return {"message": "Plan completed", "plan": plan.model_dump()}


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


@router.post("/plans/{plan_id}/approve")
async def approve_plan(plan_id: str, background_tasks: BackgroundTasks):
    """用户确认计划，开始执行"""
    from app.main import websocket_manager
    coordinator.set_websocket_manager(websocket_manager)

    plan = coordinator.approve_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    # 启动执行
    async def run_execute():
        try:
            await coordinator.execute_plan(plan_id)
        except Exception as e:
            print(f"[Pipeline] Error executing plan {plan_id}: {e}")

    background_tasks.add_task(run_execute)

    return {"status": "approved", "plan_id": plan_id, "message": "计划已确认，开始执行"}


@router.post("/plans/{plan_id}/reject")
async def reject_plan(plan_id: str, feedback: str = ""):
    """用户拒绝计划，重新讨论"""
    from app.main import websocket_manager
    coordinator.set_websocket_manager(websocket_manager)

    plan = coordinator.reject_plan(plan_id, feedback)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    return {"status": "rejected", "plan_id": plan_id, "message": "计划已拒绝，返回讨论阶段"}


@router.post("/plans/{plan_id}/iterations/{round_number}/approve")
async def approve_iteration(plan_id: str, round_number: int, background_tasks: BackgroundTasks):
    """用户确认迭代计划，开始执行"""
    from app.main import websocket_manager
    coordinator.set_websocket_manager(websocket_manager)

    iteration = coordinator.approve_iteration_plan(plan_id, round_number)
    if not iteration:
        raise HTTPException(status_code=404, detail="Iteration not found")

    plan = coordinator.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    # 启动迭代执行
    async def run_iteration_execute():
        try:
            existing_code = output_manager.read_existing_code(plan_id)
            await coordinator._execute_iteration_plan(plan_id, iteration, existing_code)
        except Exception as e:
            print(f"[Pipeline] Error executing iteration {plan_id}/{round_number}: {e}")

    background_tasks.add_task(run_iteration_execute)

    return {
        "status": "approved",
        "plan_id": plan_id,
        "iteration_round": round_number,
        "message": "迭代计划已确认，开始执行"
    }


@router.post("/plans/{plan_id}/iterations/{round_number}/reject")
async def reject_iteration(plan_id: str, round_number: int, feedback: str = ""):
    """用户拒绝迭代计划，重新讨论"""
    from app.main import websocket_manager
    coordinator.set_websocket_manager(websocket_manager)

    iteration = coordinator.reject_iteration_plan(plan_id, round_number, feedback)
    if not iteration:
        raise HTTPException(status_code=404, detail="Iteration not found")

    return {
        "status": "rejected",
        "plan_id": plan_id,
        "iteration_round": round_number,
        "message": "迭代计划已拒绝，返回讨论阶段"
    }


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


@router.get("/output/{plan_id}/files/{file_path:path}")
async def get_output_file(plan_id: str, file_path: str):
    """Get a specific output file, including nested ts-app dist assets."""
    try:
        output_dir = output_manager.get_output_path(plan_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Output path error: {str(e)}")

    requested_path = os.path.normpath(file_path).lstrip("/")
    if requested_path.startswith(".."):
        raise HTTPException(status_code=400, detail="Invalid file path")

    plan = coordinator.get_plan(plan_id)
    plan_title = getattr(plan, "title", "Output") if plan else "Output"
    target_output = getattr(plan, "target_output", None) if plan else None

    filepath = os.path.abspath(os.path.join(output_dir, requested_path))
    output_root = os.path.abspath(output_dir)
    if filepath != output_root and not filepath.startswith(output_root + os.sep):
        raise HTTPException(status_code=400, detail="Invalid file path")

    if requested_path == "index.html":
        needs_rebuild = (not os.path.exists(filepath)) or output_manager.is_misleading_placeholder_index(plan_id)

        if needs_rebuild:
            try:
                if output_manager.consolidate_web_app(plan_id, plan_title):
                    filepath = os.path.join(output_dir, requested_path)
                    if os.path.exists(filepath) and not output_manager.is_misleading_placeholder_index(plan_id):
                        return FileResponse(filepath)
            except Exception as e:
                import traceback
                traceback.print_exc()
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to generate index.html: {str(e)}",
                )

        if output_manager.is_misleading_placeholder_index(plan_id):
            validation = output_manager.read_web_validation(plan_id)
            raise HTTPException(
                status_code=409,
                detail={
                    "message": "Latest generated HTML is invalid; placeholder preview suppressed",
                    "plan_id": plan_id,
                    "invalid_candidate": "index.invalid.candidate.html",
                    "errors": (validation or {}).get("errors", [])[:5],
                    "warnings": (validation or {}).get("warnings", [])[:5],
                },
            )

        if not os.path.exists(filepath):
            validation = output_manager.read_web_validation(plan_id)
            if validation and validation.get("passed") is False:
                raise HTTPException(
                    status_code=409,
                    detail={
                        "message": "index.html was not generated because the latest candidate failed validation",
                        "plan_id": plan_id,
                        "invalid_candidate": "index.invalid.candidate.html",
                        "errors": validation.get("errors", [])[:5],
                        "warnings": validation.get("warnings", [])[:5],
                    },
                )
            raise HTTPException(status_code=404, detail="index.html not found and could not be generated from fragments")

    if target_output == "ts-app" and requested_path.startswith("ts_app/dist/") and not os.path.exists(filepath):
        output_manager.consolidate_ts_app(plan_id, plan_title)
        filepath = os.path.abspath(os.path.join(output_dir, requested_path))

    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(filepath)


@router.post("/output/{plan_id}/fix-html")
async def fix_output_html(plan_id: str, file_path: str = "index.html"):
    """Fix common syntax errors in LLM-generated HTML files.

    This endpoint automatically fixes issues like:
    - Missing spaces in CSS (padding:14px0 → padding:14px 0)
    - Missing spaces in SVG viewBox (viewBox='00512512' → viewBox='0 0 512 512')
    - Missing spaces in JS switch cases (case0: → case 0:)
    - Merged font declarations ('20052px' → '200 52px')

    Args:
        plan_id: The plan ID (first 8 chars used for directory)
        file_path: The HTML file to fix (default: index.html)

    Returns:
        Fix result with details of what was changed
    """
    from app.utils.html_fixer import fix_html_file

    try:
        output_dir = output_manager.get_output_path(plan_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Output path error: {str(e)}")

    requested_path = os.path.normpath(file_path).lstrip("/")
    if requested_path.startswith(".."):
        raise HTTPException(status_code=400, detail="Invalid file path")

    filepath = os.path.abspath(os.path.join(output_dir, requested_path))
    output_root = os.path.abspath(output_dir)
    if filepath != output_root and not filepath.startswith(output_root + os.sep):
        raise HTTPException(status_code=400, detail="Invalid file path")

    # If index.html doesn't exist, try multiple candidate paths
    if not os.path.exists(filepath) and file_path == "index.html":
        # Try ts_app/index.html for TypeScript projects
        ts_app_index = os.path.join(output_dir, "ts_app", "index.html")
        if os.path.exists(ts_app_index):
            filepath = ts_app_index
        else:
            # Try root invalid candidate
            invalid_candidate = os.path.join(output_dir, "index.invalid.candidate.html")
            if os.path.exists(invalid_candidate):
                filepath = invalid_candidate
            else:
                # Try ts_app invalid candidate for TypeScript projects
                ts_invalid = os.path.join(output_dir, "ts_app", "index.invalid.candidate.html")
                if os.path.exists(ts_invalid):
                    filepath = ts_invalid

    if not os.path.exists(filepath):
        raise HTTPException(
            status_code=404,
            detail=f"文件不存在: {file_path}。请先生成代码。"
        )

    if not filepath.endswith('.html'):
        raise HTTPException(status_code=400, detail="只能修复 HTML 文件")

    try:
        result = fix_html_file(filepath, backup=True)

        # If we fixed the invalid candidate, always copy it to index.html
        # (whether or not there were changes - the file should be usable now)
        if "invalid.candidate" in filepath:
            # Determine the correct index.html path based on where the candidate was found
            if "ts_app" in filepath:
                index_path = os.path.join(output_dir, "ts_app", "index.html")
            else:
                index_path = os.path.join(output_dir, "index.html")
            shutil.copy2(filepath, index_path)
            print(f"[fix-html] Copied fixed candidate to {index_path}")

        return {
            "success": True,
            "plan_id": plan_id,
            "file_path": file_path,
            "fix_result": result.to_dict()
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"修复失败: {str(e)}")


@router.get("/output/{plan_id}/preview")
async def get_output_preview(plan_id: str):
    """Get preview URL for the generated output."""
    plan = coordinator.get_plan(plan_id)
    target_output = getattr(plan, "target_output", None) if plan else None
    plan_title = getattr(plan, "title", "Output") if plan else "Output"

    preview_entry = output_manager.resolve_preview_entry(plan_id, target_output)
    if not preview_entry and target_output == "ts-app":
        output_manager.consolidate_ts_app(plan_id, plan_title)
        preview_entry = output_manager.resolve_preview_entry(plan_id, target_output)

    if preview_entry:
        return {
            "preview_url": f"/api/pipeline/output/{plan_id}/files/{preview_entry}",
            "has_preview": True
        }

    if target_output == "web-app" and output_manager.is_misleading_placeholder_index(plan_id):
        validation = output_manager.read_web_validation(plan_id)
        return {
            "has_preview": False,
            "message": "Latest generated HTML is invalid; placeholder preview suppressed",
            "invalid_candidate": "index.invalid.candidate.html",
            "errors": (validation or {}).get("errors", [])[:5],
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
            if not plan.skip_discussion:
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
            if not plan.skip_discussion:
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


@router.post("/restart/{plan_id}/iteration/{round_number}")
async def restart_iteration(plan_id: str, round_number: int, background_tasks: BackgroundTasks):
    """Restart a specific iteration round: clear its tasks and discussion, then re-run"""
    from app.main import websocket_manager

    coordinator.set_websocket_manager(websocket_manager)

    plan = coordinator.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    # Find the iteration
    iteration = None
    for iter_round in plan.iterations:
        if iter_round.round_number == round_number:
            iteration = iter_round
            break

    if not iteration:
        raise HTTPException(status_code=404, detail=f"Iteration round {round_number} not found")

    # Reset the iteration
    iteration.status = PlanStatus.DRAFT
    iteration.tasks = []
    iteration.discussion = []
    iteration.completed_at = None
    plan.status = PlanStatus.EXECUTING
    plan.current_iteration_round = round_number
    coordinator._save_plans()

    # Run iteration in background
    async def run_iteration_background():
        try:
            existing_code = output_manager.read_existing_code(plan_id)
            await coordinator._analyze_iteration_request(plan_id, iteration, existing_code, iteration.iteration_request)
            if not plan.skip_discussion:
                await coordinator._organize_iteration_discussion(plan_id, iteration, existing_code, iteration.iteration_request)
            await coordinator._generate_iteration_plan(plan_id, iteration, existing_code, iteration.iteration_request)
            await coordinator._execute_iteration_plan(plan_id, iteration, existing_code)
        except Exception as e:
            print(f"[Pipeline] Error in restarted iteration {plan_id}/{round_number}: {e}")

    background_tasks.add_task(run_iteration_background)

    return {
        "message": f"Iteration round {round_number} restarted",
        "plan_id": plan_id,
        "iteration_round": round_number,
    }


@router.post("/stop/{plan_id}/iteration/{round_number}")
async def stop_iteration(plan_id: str, round_number: int):
    """停止正在执行的迭代"""
    from app.main import websocket_manager
    from datetime import datetime

    plan = coordinator.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    # 查找指定迭代
    iteration = None
    for it in plan.iterations:
        if it.round_number == round_number:
            iteration = it
            break

    if not iteration:
        raise HTTPException(status_code=404, detail=f"Iteration {round_number} not found")

    # 如果已经在执行中，设置停止标志
    if iteration.status == PlanStatus.EXECUTING:
        coordinator.request_stop_iteration(plan_id, round_number)
        return {
            "message": f"Stop request sent for iteration {round_number}",
            "plan_id": plan_id,
            "iteration_round": round_number,
        }

    # 如果不是执行中，直接强制完成
    if iteration.status in [PlanStatus.APPROVED, PlanStatus.DISCUSSING, PlanStatus.DRAFT]:
        iteration.status = PlanStatus.COMPLETED
        iteration.completed_at = datetime.utcnow()
        coordinator._save_plans()

        # 广播更新
        if websocket_manager:
            await websocket_manager.broadcast({
                "type": "plan_update",
                "data": {
                    "plan_id": plan_id,
                    "plan": plan.model_dump(),
                    "status": "completed",
                    "iteration_round": round_number,
                    "stopped": True,
                }
            })

        return {
            "message": f"Iteration {round_number} force stopped",
            "plan_id": plan_id,
            "iteration_round": round_number,
        }

    # 已完成状态：返回成功（而不是报错）
    if iteration.status == PlanStatus.COMPLETED:
        return {
            "message": f"Iteration {round_number} is already completed",
            "plan_id": plan_id,
            "iteration_round": round_number,
        }

    # 其他未知状态
    raise HTTPException(
        status_code=400,
        detail=f"Iteration is in unexpected state: {iteration.status}"
    )


@router.post("/resume/{plan_id}/iteration/{round_number}")
async def resume_iteration(plan_id: str, round_number: int, background_tasks: BackgroundTasks):
    """Resume an interrupted iteration from its current state"""
    from app.main import websocket_manager

    coordinator.set_websocket_manager(websocket_manager)

    plan = coordinator.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    # Find the iteration
    iteration = None
    for iter_round in plan.iterations:
        if iter_round.round_number == round_number:
            iteration = iter_round
            break

    if not iteration:
        raise HTTPException(status_code=404, detail=f"Iteration round {round_number} not found")

    # Re-assign agents to tasks
    coordinator._reassign_agents(plan_id)

    # Reset running tasks to pending
    for task in iteration.tasks:
        if task.status == TaskStatus.RUNNING:
            task.status = TaskStatus.PENDING

    # Set plan status
    plan.status = PlanStatus.EXECUTING
    plan.current_iteration_round = round_number
    coordinator._save_plans()

    # Run iteration execution in background
    async def run_iteration_execution():
        try:
            existing_code = output_manager.read_existing_code(plan_id)

            if iteration.status == PlanStatus.DRAFT:
                # Need to run full iteration pipeline
                await coordinator._analyze_iteration_request(plan_id, iteration, existing_code, iteration.iteration_request)
                if not plan.skip_discussion:
                    await coordinator._organize_iteration_discussion(plan_id, iteration, existing_code, iteration.iteration_request)
                await coordinator._generate_iteration_plan(plan_id, iteration, existing_code, iteration.iteration_request)
            elif iteration.status == PlanStatus.DISCUSSING:
                # Resume from discussion
                if not plan.skip_discussion:
                    await coordinator._organize_iteration_discussion(plan_id, iteration, existing_code, iteration.iteration_request)
                await coordinator._generate_iteration_plan(plan_id, iteration, existing_code, iteration.iteration_request)
            elif iteration.status == PlanStatus.APPROVED:
                # Just execute the plan
                pass  # Will execute below

            # Execute the iteration
            await coordinator._execute_iteration_plan(plan_id, iteration, existing_code)
        except Exception as e:
            print(f"[Pipeline] Error resuming iteration {plan_id}/{round_number}: {e}")

    background_tasks.add_task(run_iteration_execution)

    return {
        "message": f"Iteration round {round_number} resumed",
        "plan_id": plan_id,
        "iteration_round": round_number,
        "phase": iteration.status,
    }


@router.get("/task/{task_id}")
async def get_task_status_endpoint(task_id: str):
    """Get the status of a task (deprecated - Celery no longer used)"""
    return {
        "task_id": task_id,
        "status": "deprecated",
        "message": "Celery tasks are no longer used. Use /plans/{plan_id} to check pipeline status."
    }


@router.post("/iterate/{plan_id}")
async def iterate_plan(plan_id: str, request: IterationRequest, background_tasks: BackgroundTasks):
    """对已完成的 plan 进行迭代

    完整流程：分析 -> 讨论 -> 计划 -> 执行
    创建新的迭代轮次，生成针对迭代的任务列表。
    """
    from app.main import websocket_manager

    coordinator.set_websocket_manager(websocket_manager)

    plan = coordinator.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    if plan.status != PlanStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail=f"Plan is not completed (status: {plan.status}). Only completed plans can be iterated."
        )

    # Run iteration in background
    async def run_iteration_background():
        try:
            await coordinator.iterate_plan(plan_id, request.iteration_request)
        except Exception as e:
            print(f"[Pipeline] Error in iteration {plan_id}: {e}")
            import traceback
            traceback.print_exc()

    background_tasks.add_task(run_iteration_background)

    return {
        "message": "Iteration started",
        "plan_id": plan_id,
        "iteration_request": request.iteration_request,
    }


@router.post("/archives/{plan_id}/create")
async def create_archive(plan_id: str, request: CreateArchiveRequest = CreateArchiveRequest()):
    """手动创建当前版本的存档

    Args:
        plan_id: 计划 ID
        request: 存档创建请求，包含可选的自定义名称和描述
    """
    plan = coordinator.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    # 检查是否有生成的代码
    plan_dir = os.path.join(output_manager.base_dir, plan_id[:8])
    index_path = os.path.join(plan_dir, "index.html")
    if not os.path.exists(index_path):
        raise HTTPException(
            status_code=400,
            detail="No code generated yet. Please complete at least one task first."
        )

    # 确定存档轮次
    if request.round_number is not None:
        round_number = request.round_number
    else:
        # 使用当前迭代轮次，如果没有迭代则使用0
        round_number = plan.current_iteration_round if plan.current_iteration_round > 0 else 0

    # 检查是否已存在该轮次的存档，如果存在则生成新的轮次号
    existing_archives = output_manager.list_archives(plan_id)
    existing_rounds = {a["round_number"] for a in existing_archives}

    original_round = round_number
    suffix = 1
    while round_number in existing_rounds:
        # 对于手动存档，使用 special naming
        round_number = 10000 + original_round * 100 + suffix  # 手动存档使用10000+的编号
        suffix += 1

    # 创建存档
    archive_path = output_manager.save_iteration_archive(
        plan_id,
        round_number,
        custom_name=request.custom_name,
        description=request.description or f"手动存档 - {request.custom_name or f'Version {round_number}'}"
    )

    if not archive_path:
        raise HTTPException(
            status_code=500,
            detail="Failed to create archive"
        )

    return {
        "message": "Archive created successfully",
        "plan_id": plan_id,
        "round_number": round_number,
        "archive_path": archive_path,
        "custom_name": request.custom_name,
        "description": request.description,
    }


@router.get("/archives/{plan_id}")
async def list_archives(plan_id: str):
    """获取 plan 的所有存档版本"""
    plan = coordinator.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    archives = output_manager.list_archives(plan_id)
    return {
        "plan_id": plan_id,
        "archives": archives,
        "total": len(archives),
    }


@router.post("/archives/{plan_id}/restore/{round_number}")
async def restore_archive(plan_id: str, round_number: int):
    """还原到指定存档版本

    Args:
        plan_id: 计划 ID
        round_number: 迭代轮次（0 表示初始版本）
    """
    plan = coordinator.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    # 检查存档是否存在
    archives = output_manager.list_archives(plan_id)
    target_archive = next((a for a in archives if a["round_number"] == round_number), None)

    if not target_archive:
        raise HTTPException(
            status_code=404,
            detail=f"Archive for round {round_number} not found"
        )

    # 执行还原
    success = output_manager.restore_iteration_archive(plan_id, round_number)

    if not success:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to restore archive for round {round_number}"
        )

    return {
        "message": f"Successfully restored to {'initial version' if round_number == 0 else f'iteration {round_number}'}",
        "plan_id": plan_id,
        "restored_round": round_number,
        "archive_info": target_archive,
    }


@router.delete("/archives/{plan_id}/{round_number}")
async def delete_archive(plan_id: str, round_number: int):
    """删除指定存档版本

    Args:
        plan_id: 计划 ID
        round_number: 迭代轮次（0 表示初始版本）
    """
    plan = coordinator.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    # 检查存档是否存在
    archives = output_manager.list_archives(plan_id)
    target_archive = next((a for a in archives if a["round_number"] == round_number), None)

    if not target_archive:
        raise HTTPException(
            status_code=404,
            detail=f"Archive for round {round_number} not found"
        )

    # 执行删除
    success = output_manager.delete_archive(plan_id, round_number)

    if not success:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete archive for round {round_number}"
        )

    return {
        "message": f"Successfully deleted {'initial version' if round_number == 0 else f'iteration {round_number}'} archive",
        "plan_id": plan_id,
        "deleted_round": round_number,
    }


@router.get("/archives/{plan_id}/download/{round_number}")
async def download_archive(plan_id: str, round_number: int):
    """下载存档为 zip 文件

    Args:
        plan_id: 计划 ID
        round_number: 迭代轮次
    """
    plan = coordinator.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    zip_path = output_manager.get_archive_as_zip(plan_id, round_number)

    if not zip_path or not os.path.exists(zip_path):
        raise HTTPException(
            status_code=404,
            detail=f"Archive for round {round_number} not found or failed to create zip"
        )

    # 确定下载文件名
    if round_number == 0:
        filename = f"archive_{plan_id[:8]}_initial.zip"
    else:
        filename = f"archive_{plan_id[:8]}_iteration_{round_number}.zip"

    return FileResponse(
        zip_path,
        media_type="application/zip",
        filename=filename
    )


@router.post("/archives/{plan_id}/diff")
async def get_archive_diff(plan_id: str, request: ArchiveDiffRequest):
    """对比两个存档版本的差异

    Args:
        plan_id: 计划 ID
        request: 包含 from_round 和 to_round 的请求体
    """
    plan = coordinator.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    diff_result = output_manager.get_archive_diff(plan_id, request.from_round, request.to_round)

    if "errors" in diff_result:
        raise HTTPException(status_code=400, detail=diff_result["errors"])

    return diff_result


@router.get("/archives/{plan_id}/validate/{round_number}")
async def validate_archive(plan_id: str, round_number: int):
    """验证存档完整性

    Args:
        plan_id: 计划 ID
        round_number: 迭代轮次
    """
    plan = coordinator.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    validation_result = output_manager.validate_archive(plan_id, round_number)

    return validation_result


@router.get("/archives/{plan_id}/content/{round_number}")
async def get_archive_content(plan_id: str, round_number: int):
    """获取存档内容（用于预览）

    Args:
        plan_id: 计划 ID
        round_number: 迭代轮次
    """
    plan = coordinator.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    content = output_manager.get_archive_content(plan_id, round_number)

    if content is None:
        raise HTTPException(
            status_code=404,
            detail=f"Archive content for round {round_number} not found"
        )

    return {
        "plan_id": plan_id,
        "round_number": round_number,
        "content": content,
        "size": len(content),
    }


@router.get("/output/{plan_id}/godot")
async def get_godot_project(plan_id: str):
    """Get Godot project info for a plan

    Returns file list and validation status
    """
    plan = coordinator.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    if plan.target_output != "godot-game":
        raise HTTPException(
            status_code=400,
            detail=f"This plan is not a Godot project (target_output: {plan.target_output})"
        )

    project_info = output_manager.get_godot_project_info(plan_id)

    return {
        "plan_id": plan_id,
        "plan_title": plan.title,
        "target_output": plan.target_output,
        "project": project_info
    }


@router.get("/output/{plan_id}/godot/download")
async def download_godot_project(plan_id: str):
    """Download Godot project as zip file

    Returns the project files packaged as a zip archive
    """
    plan = coordinator.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    if plan.target_output != "godot-game":
        raise HTTPException(
            status_code=400,
            detail=f"This plan is not a Godot project (target_output: {plan.target_output})"
        )

    zip_path = output_manager.get_godot_project_zip(plan_id)

    if not zip_path or not os.path.exists(zip_path):
        raise HTTPException(
            status_code=404,
            detail="Godot project not found or failed to create zip"
        )

    filename = f"godot_project_{plan_id[:8]}.zip"

    return FileResponse(
        zip_path,
        media_type="application/zip",
        filename=filename
    )


@router.get("/output/{plan_id}/ts-app")
async def get_ts_app_project(plan_id: str):
    """Get ts-app project metadata and validation status."""
    plan = coordinator.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    if plan.target_output != "ts-app":
        raise HTTPException(
            status_code=400,
            detail=f"This plan is not a TypeScript app project (target_output: {plan.target_output})"
        )

    project_info = output_manager.get_ts_app_project_info(plan_id)
    return {
        "plan_id": plan_id,
        "plan_title": plan.title,
        "target_output": plan.target_output,
        "project": project_info,
    }


@router.get("/output/{plan_id}/ts-app/download")
async def download_ts_app_project(plan_id: str):
    """Download ts-app project as zip file."""
    plan = coordinator.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    if plan.target_output != "ts-app":
        raise HTTPException(
            status_code=400,
            detail=f"This plan is not a TypeScript app project (target_output: {plan.target_output})"
        )

    zip_path = output_manager.get_ts_app_project_zip(plan_id)
    if not zip_path or not os.path.exists(zip_path):
        raise HTTPException(
            status_code=404,
            detail="TypeScript app project not found or failed to create zip"
        )

    filename = f"ts_app_project_{plan_id[:8]}.zip"
    return FileResponse(
        zip_path,
        media_type="application/zip",
        filename=filename
    )
