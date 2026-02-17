from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class AgentType(str, Enum):
    CODER = "coder"
    ANALYST = "analyst"
    ASSISTANT = "assistant"
    CUSTOM = "custom"


class AgentStatus(str, Enum):
    IDLE = "idle"
    WORKING = "working"
    WAITING = "waiting"
    ERROR = "error"


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    type: AgentType = AgentType.ASSISTANT
    description: Optional[str] = None
    custom_prompt: Optional[str] = None
    position: Dict[str, float] = Field(default_factory=lambda: {"x": 0, "y": 0, "z": 0})


class AgentCreate(AgentBase):
    pass


class AgentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    custom_prompt: Optional[str] = None
    position: Optional[Dict[str, float]] = None
    status: Optional[AgentStatus] = None


class Agent(AgentBase):
    id: str
    status: AgentStatus = AgentStatus.IDLE
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    current_task_id: Optional[str] = None

    class Config:
        from_attributes = True


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    agent_id: Optional[str] = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    progress: Optional[float] = None
    result: Optional[str] = None


class Task(TaskBase):
    id: str
    status: TaskStatus = TaskStatus.PENDING
    progress: float = 0.0
    result: Optional[str] = None
    thinking_process: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ChatMessage(BaseModel):
    id: str
    agent_id: str
    role: str  # "user" or "agent"
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class WebSocketMessage(BaseModel):
    type: str  # "task_update", "agent_update", "thinking", "chat"
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ThinkingStep(BaseModel):
    step: int
    thought: str
    action: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
