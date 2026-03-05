"""
Agent Stats API

Endpoints for retrieving agent statistics, achievements, and growth data.
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, List

from app.services.agent_growth_service import growth_service
from app.services.achievement_service import get_achievement_service
from app.services.motivation_service import motivation_service

router = APIRouter(prefix="/agents", tags=["stats"])


@router.get("/{agent_id}/stats")
async def get_agent_stats(agent_id: str) -> Dict:
    """
    Get stats for a specific agent.

    Returns:
        AgentStats including level, XP, motivation, and achievements
    """
    stats = growth_service.get_agent_stats(agent_id)

    # Add emotion state
    emotion_state = motivation_service.get_emotion_state(stats.motivation)

    return {
        **stats.model_dump(),
        "emotion_state": {
            "key": emotion_state[0],
            "emoji": emotion_state[1],
            "label": emotion_state[2]
        }
    }


@router.get("/stats")
async def get_all_agent_stats() -> Dict[str, Dict]:
    """
    Get stats for all agents.

    Returns:
        Dictionary mapping agent_id to AgentStats
    """
    all_stats = growth_service.get_all_stats()

    # Add emotion state to each
    result = {}
    for agent_id, stats in all_stats.items():
        motivation = stats.get("motivation", 0.5)
        emotion_state = motivation_service.get_emotion_state(motivation)
        result[agent_id] = {
            **stats,
            "emotion_state": {
                "key": emotion_state[0],
                "emoji": emotion_state[1],
                "label": emotion_state[2]
            }
        }

    return result


@router.get("/{agent_id}/achievements")
async def get_agent_achievements(agent_id: str) -> List[Dict]:
    """
    Get achievements unlocked by a specific agent.

    Returns:
        List of achievement objects
    """
    achievement_service = get_achievement_service()
    return achievement_service.get_agent_achievements(agent_id)


@router.get("/{agent_id}/achievements/progress")
async def get_achievement_progress(agent_id: str) -> Dict:
    """
    Get achievement progress for a specific agent.

    Returns:
        Dictionary mapping achievement_id to progress info
    """
    stats = growth_service.get_agent_stats(agent_id)
    achievement_service = get_achievement_service()

    return achievement_service.get_achievement_progress(
        agent_id,
        stats.model_dump()
    )


@router.get("/achievements")
async def get_all_achievements() -> Dict[str, Dict]:
    """
    Get all achievement definitions.

    Returns:
        Dictionary of all achievements
    """
    achievement_service = get_achievement_service()
    return achievement_service.get_all_achievements()
