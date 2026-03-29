from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from app.models.schemas import AgentCreate, AgentUpdate, Agent
from app.services.agent_manager import agent_manager
from app.services.workspace_manager import workspace_manager
from app.agents.base import BaseAgent

router = APIRouter(prefix="/agents", tags=["agents"])


def agent_to_response(agent: BaseAgent) -> dict:
    return agent.to_dict()


@router.post("", response_model=dict)
async def create_agent(agent_data: AgentCreate):
    """Create a new agent"""
    agent = agent_manager.create_agent(
        name=agent_data.name,
        agent_type=agent_data.type,
        description=agent_data.description,
        custom_prompt=agent_data.custom_prompt,
        position=agent_data.position,
        display_type=agent_data.display_type,
    )
    return agent_to_response(agent)


@router.get("", response_model=List[dict])
async def list_agents():
    """List all agents"""
    agents = agent_manager.get_all_agents()
    return [agent_to_response(a) for a in agents]


@router.get("/{agent_id}", response_model=dict)
async def get_agent(agent_id: str):
    """Get agent by ID"""
    agent = agent_manager.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent_to_response(agent)


@router.put("/{agent_id}", response_model=dict)
async def update_agent(agent_id: str, agent_data: AgentUpdate):
    """Update agent"""
    agent = agent_manager.update_agent(
        agent_id,
        name=agent_data.name,
        description=agent_data.description,
        custom_prompt=agent_data.custom_prompt,
        position=agent_data.position,
        status=agent_data.status,
        display_type=agent_data.display_type,
        tags=agent_data.tags,
    )
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent_to_response(agent)


@router.delete("/{agent_id}")
async def delete_agent(agent_id: str):
    """Delete agent"""
    if not agent_manager.delete_agent(agent_id):
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"message": "Agent deleted successfully"}


# === Workspace Management Endpoints ===

class WorkspaceFileUpdate(BaseModel):
    content: str


@router.get("/{agent_id}/workspace")
async def get_agent_workspace(agent_id: str):
    """获取 Agent 的 workspace 文件内容"""
    agent = agent_manager.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    files = workspace_manager.get_workspace_files(agent_id)
    if not files:
        raise HTTPException(status_code=404, detail="Workspace not found")

    return {"agent_id": agent_id, "files": files}


@router.put("/{agent_id}/workspace/{filename}")
async def update_workspace_file(agent_id: str, filename: str, data: WorkspaceFileUpdate):
    """更新 workspace 中的指定文件"""
    agent = agent_manager.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    success = workspace_manager.update_workspace_file(agent_id, filename, data.content)
    if not success:
        raise HTTPException(status_code=400, detail=f"Cannot update file: {filename}")

    return {"message": f"File {filename} updated successfully"}
