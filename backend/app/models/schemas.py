from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class AgentType(str, Enum):
    CODER = "coder"
    ANALYST = "analyst"
    ASSISTANT = "assistant"
    TESTER = "tester"
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


class PlanStatus(str, Enum):
    DRAFT = "draft"
    DISCUSSING = "discussing"
    APPROVED = "approved"
    EXECUTING = "executing"
    COMPLETED = "completed"


class AgentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    type: AgentType = AgentType.ASSISTANT
    display_type: Optional[str] = None  # 自定义显示名称，如 "UI设计师"
    description: Optional[str] = None
    custom_prompt: Optional[str] = None
    position: Dict[str, float] = Field(default_factory=lambda: {"x": 0, "y": 0, "z": 0})


class AgentCreate(AgentBase):
    pass


class AgentUpdate(BaseModel):
    name: Optional[str] = None
    display_type: Optional[str] = None  # 允许更新自定义类型名称
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
    parent_task_id: Optional[str] = None


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


# Discussion system
class DiscussionMessage(BaseModel):
    id: str
    plan_id: str
    agent_id: str
    agent_name: str
    agent_type: str
    content: str
    message_type: str = "comment"  # comment, proposal, question, answer, agreement
    reply_to: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class DiscussionMessageCreate(BaseModel):
    content: str
    message_type: str = "comment"
    reply_to: Optional[str] = None


# Plan system
class PlanTask(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    assigned_agent_id: Optional[str] = None
    assigned_agent_type: Optional[str] = None
    dependencies: List[str] = Field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    order: int = 0


class PlanBase(BaseModel):
    title: str
    description: Optional[str] = None
    original_request: str
    target_output: Optional[str] = None  # e.g., "web-app", "api", "report"


class PlanCreate(PlanBase):
    pass


class PlanUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[PlanStatus] = None
    tasks: Optional[List[PlanTask]] = None
    is_approved: Optional[bool] = None


class Plan(PlanBase):
    id: str
    status: PlanStatus = PlanStatus.DRAFT
    tasks: List[PlanTask] = Field(default_factory=list)
    discussion: List[DiscussionMessage] = Field(default_factory=list)
    is_approved: bool = False
    created_by_agent_id: Optional[str] = None
    selected_agent_ids: List[str] = Field(default_factory=list)  # Agent IDs selected for this plan
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
    type: str  # "task_update", "agent_update", "thinking", "chat", "discussion", "plan_update"
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ThinkingStep(BaseModel):
    step: int
    thought: str
    action: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Pipeline request
class PipelineRequest(BaseModel):
    request: str
    target_output: str = "web-app"  # web-app, api, report, etc.
    selected_agent_ids: List[str] = Field(default_factory=list)  # Agent IDs to use in pipeline


class IterationRequest(BaseModel):
    """Request to iterate on a completed plan"""
    iteration_request: str = Field(..., min_length=1, max_length=2000)
