from fastapi import APIRouter, HTTPException
from typing import List
from app.models.schemas import AgentCreate, AgentUpdate, Agent
from app.services.agent_manager import agent_manager
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
