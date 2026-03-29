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
    # PUA 增强版
    PUA_CODER = "pua-coder"
    PUA_ANALYST = "pua-analyst"
    PUA_ASSISTANT = "pua-assistant"
    PUA_TESTER = "pua-tester"


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


class TaskPriority(str, Enum):
    P0 = "p0"  # Urgent
    P1 = "p1"  # High
    P2 = "p2"  # Medium
    P3 = "p3"  # Low


class PlanStatus(str, Enum):
    DRAFT = "draft"
    DISCUSSING = "discussing"
    PENDING_APPROVAL = "pending_approval"  # 计划已生成，等待用户确认
    APPROVED = "approved"     # 用户已确认
    EXECUTING = "executing"
    COMPLETED = "completed"


class AgentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    type: AgentType = AgentType.ASSISTANT
    display_type: Optional[str] = None  # 自定义显示名称，如 "UI设计师"
    description: Optional[str] = None
    custom_prompt: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    position: Dict[str, float] = Field(default_factory=lambda: {"x": 0, "y": 0, "z": 0})


class AgentCreate(AgentBase):
    pass


class AgentUpdate(BaseModel):
    name: Optional[str] = None
    display_type: Optional[str] = None  # 允许更新自定义类型名称
    description: Optional[str] = None
    custom_prompt: Optional[str] = None
    tags: Optional[List[str]] = None
    position: Optional[Dict[str, float]] = None
    status: Optional[AgentStatus] = None


class Agent(AgentBase):
    id: str
    status: AgentStatus = AgentStatus.IDLE
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    current_task_id: Optional[str] = None
    workspace_id: Optional[str] = None  # Workspace 目录标识

    class Config:
        from_attributes = True


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    agent_id: Optional[str] = None
    parent_task_id: Optional[str] = None
    priority: TaskPriority = TaskPriority.P2
    due_date: Optional[datetime] = None


class TaskCreate(TaskBase):
    priority: TaskPriority = TaskPriority.P2
    due_date: Optional[datetime] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    progress: Optional[float] = None
    result: Optional[str] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None


class Task(TaskBase):
    id: str
    status: TaskStatus = TaskStatus.PENDING
    progress: float = 0.0
    result: Optional[str] = None
    thinking_process: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
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
    timestamp: datetime = Field(default_factory=datetime.now)


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
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class IterationTask(BaseModel):
    """迭代轮次中的任务"""
    id: str
    iteration_round: int
    title: str
    description: Optional[str] = None
    assigned_agent_id: Optional[str] = None
    assigned_agent_type: Optional[str] = None
    dependencies: List[str] = Field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    order: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class IterationRound(BaseModel):
    """迭代轮次"""
    round_number: int
    iteration_request: str
    status: PlanStatus = PlanStatus.DRAFT
    tasks: List[IterationTask] = Field(default_factory=list)
    discussion: List[DiscussionMessage] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    archive_path: Optional[str] = None  # 存档路径（相对于 output 目录）


class PlanBase(BaseModel):
    title: str
    description: Optional[str] = None
    original_request: str
    target_output: Optional[str] = None  # e.g., "web-app", "ts-app", "godot-game", "api", "report"


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
    discussion_summary: Optional[str] = None  # Structured summary for Coder context
    is_approved: bool = False
    created_by_agent_id: Optional[str] = None
    selected_agent_ids: List[str] = Field(default_factory=list)  # Agent IDs selected for this plan
    iterations: List[IterationRound] = Field(default_factory=list)  # 迭代轮次列表
    current_iteration_round: int = 0  # 当前迭代轮次（0表示初始版本）
    skip_discussion: bool = False  # Persist skip_discussion setting for resume/restart
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ChatMessage(BaseModel):
    id: str
    agent_id: str
    role: str  # "user" or "agent"
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)


class WebSocketMessage(BaseModel):
    type: str  # "task_update", "agent_update", "thinking", "chat", "discussion", "plan_update"
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)


class ThinkingStep(BaseModel):
    step: int
    thought: str
    action: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


# Pipeline request
class PipelineRequest(BaseModel):
    request: str
    target_output: str = "web-app"  # web-app, ts-app, godot-game, api, report, etc.
    selected_agent_ids: List[str] = Field(default_factory=list)  # Agent IDs to use in pipeline
    skip_discussion: bool = False  # Skip discussion phase, go directly to plan generation


class IterationRequest(BaseModel):
    """Request to iterate on a completed plan"""
    iteration_request: str = Field(..., min_length=1, max_length=2000)


# Archive Management
class ArchiveInfo(BaseModel):
    """存档信息"""
    round_number: int
    label: str
    archive_name: str
    archive_path: str
    size: int
    modified_at: str
    custom_name: Optional[str] = None
    description: Optional[str] = None
    checksum: Optional[str] = None


class CreateArchiveRequest(BaseModel):
    """手动创建存档请求"""
    round_number: Optional[int] = None  # 不指定则使用当前迭代轮次+1
    custom_name: Optional[str] = None
    description: Optional[str] = None


class ArchiveDiffRequest(BaseModel):
    """差异对比请求"""
    from_round: int
    to_round: int


class ArchiveDiffResult(BaseModel):
    """差异对比结果"""
    from_round: int
    to_round: int
    from_size: int
    to_size: int
    additions: int
    deletions: int
    diff_lines: List[str] = Field(default_factory=list)


class ArchiveValidationResult(BaseModel):
    """存档验证结果"""
    round_number: int
    valid: bool
    checksum_match: bool
    file_exists: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


# Group Chat System (QQ-like)
class FileAttachment(BaseModel):
    """文件附件"""
    id: str
    filename: str
    original_name: str
    file_path: str
    file_size: int
    mime_type: str
    upload_by: str
    upload_at: datetime = Field(default_factory=datetime.now)


class GroupChatMember(BaseModel):
    """群聊成员"""
    id: str  # agent_id 或 "user"
    name: str
    type: str  # "agent" 或 "user"
    avatar_color: Optional[str] = None
    joined_at: datetime = Field(default_factory=datetime.now)


class GroupChatMessage(BaseModel):
    """群聊消息"""
    id: str
    chat_id: str
    sender_id: str
    sender_name: str
    sender_type: str  # "agent" 或 "user"
    content: str
    message_type: str = "text"  # "text", "file", "system"
    attachments: List[FileAttachment] = Field(default_factory=list)
    reply_to: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class GroupChat(BaseModel):
    """群聊"""
    id: str
    name: str
    description: Optional[str] = None
    created_by: str
    members: List[GroupChatMember] = Field(default_factory=list)
    messages: List[GroupChatMessage] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    is_active: bool = True


class GroupChatCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    agent_ids: List[str] = Field(default_factory=list)
    description: Optional[str] = None
