from fastapi import APIRouter, HTTPException
from typing import List
from app.models.schemas import TaskCreate, TaskUpdate, Task
from app.services.agent_manager import agent_manager
from app.services.task_executor import task_executor

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=dict)
async def create_task(task_data: TaskCreate):
    """Create a new task"""
    task = agent_manager.create_task(
        title=task_data.title,
        description=task_data.description,
        agent_id=task_data.agent_id,
    )
    return task.model_dump()


@router.get("", response_model=List[dict])
async def list_tasks():
    """List all tasks"""
    tasks = agent_manager.get_all_tasks()
    return [t.model_dump() for t in tasks]


@router.get("/{task_id}", response_model=dict)
async def get_task(task_id: str):
    """Get task by ID"""
    task = agent_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task.model_dump()


@router.put("/{task_id}", response_model=dict)
async def update_task(task_id: str, task_data: TaskUpdate):
    """Update task"""
    task = agent_manager.update_task(
        task_id,
        title=task_data.title,
        description=task_data.description,
        status=task_data.status,
        progress=task_data.progress,
        result=task_data.result,
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task.model_dump()


@router.delete("/{task_id}")
async def delete_task(task_id: str):
    """Delete task"""
    if not agent_manager.delete_task(task_id):
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully"}


@router.post("/{task_id}/assign/{agent_id}")
async def assign_task(task_id: str, agent_id: str):
    """Assign task to agent"""
    task = agent_manager.assign_task(task_id, agent_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task or Agent not found")
    return task.model_dump()


@router.post("/{task_id}/start")
async def start_task(task_id: str):
    """Start task execution"""
    task = agent_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if not task.agent_id:
        raise HTTPException(status_code=400, detail="Task has no assigned agent")

    # Import here to avoid circular dependency
    from app.main import websocket_manager

    task_executor.start_task(task_id, websocket_manager)
    return {"message": "Task started", "task_id": task_id}


@router.post("/{task_id}/cancel")
async def cancel_task(task_id: str):
    """Cancel task execution"""
    if task_executor.cancel_task(task_id):
        return {"message": "Task cancelled", "task_id": task_id}
    raise HTTPException(status_code=404, detail="Task not running")
