"""
Agent Statistics and Growth Data Model
Defines the data structure for tracking agent capabilities and progression.
"""

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class AgentStats(BaseModel):
    """Statistics and progression data for a single agent."""

    agent_id: str

    # Level and XP
    level: int = Field(default=1, ge=1, le=100, description="Agent level (1-100)")
    xp: int = Field(default=0, ge=0, description="Current experience points")
    xp_to_next_level: int = Field(
        default=100,
        ge=1,
        description="XP required to reach next level"
    )

    # Task Statistics
    tasks_completed: int = Field(default=0, ge=0, description="Total tasks completed")
    tasks_successful: int = Field(
        default=0, ge=0, description="Tasks completed without retries"
    )
    quality_streak: int = Field(
        default=0, ge=0, description="Consecutive A-grade tasks"
    )
    pipeline_count: int = Field(
        default=0, ge=0, description="Number of pipelines participated in"
    )

    # Motivation and Satisfaction (0.0 - 1.0)
    motivation: float = Field(
        default=0.5, ge=0.0, le=1.0, description="Current motivation level"
    )
    satisfaction: float = Field(
        default=0.5, ge=0.0, le=1.0, description="Current satisfaction level"
    )

    # Achievements
    achievements: List[str] = Field(default_factory=list, description="Unlocked achievements")
    unlocked_at: Dict[str, datetime] = Field(
        default_factory=dict, description="Timestamps for achievement unlocks"
    )

    # Timestamps
    last_motivation_decay: Optional[datetime] = Field(
        default=None, description="Last time motivation decay was applied"
    )
    created_at: datetime = Field(
        default_factory=datetime.now, description="When this stats record was created"
    )
    updated_at: datetime = Field(
        default_factory=datetime.now, description="Last update timestamp"
    )

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }

    def model_dump(self, **kwargs):
        """Custom serialization to handle datetime conversion."""
        data = super().model_dump(**kwargs)
        if isinstance(data.get('last_motivation_decay'), datetime):
            data['last_motivation_decay'] = data['last_motivation_decay'].isoformat()
        if isinstance(data.get('created_at'), datetime):
            data['created_at'] = data['created_at'].isoformat()
        if isinstance(data.get('updated_at'), datetime):
            data['updated_at'] = data['updated_at'].isoformat()
        if isinstance(data.get('unlocked_at'), dict):
            data['unlocked_at'] = {
                k: v.isoformat() if isinstance(v, datetime) else v
                for k, v in data['unlocked_at'].items()
            }
        return data

    @classmethod
    def model_validate(cls, obj):
        """Custom deserialization to handle datetime parsing."""
        if isinstance(obj, dict):
            # Parse datetime fields from ISO format strings
            if isinstance(obj.get('last_motivation_decay'), str):
                obj['last_motivation_decay'] = datetime.fromisoformat(
                    obj['last_motivation_decay']
                )
            if isinstance(obj.get('created_at'), str):
                obj['created_at'] = datetime.fromisoformat(obj['created_at'])
            if isinstance(obj.get('updated_at'), str):
                obj['updated_at'] = datetime.fromisoformat(obj['updated_at'])
            if isinstance(obj.get('unlocked_at'), dict):
                obj['unlocked_at'] = {
                    k: datetime.fromisoformat(v) if isinstance(v, str) else v
                    for k, v in obj['unlocked_at'].items()
                }
        return super().model_validate(obj)
