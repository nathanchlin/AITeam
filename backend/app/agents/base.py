from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, AsyncGenerator
from datetime import datetime
import uuid
from app.models.schemas import AgentType, AgentStatus, Agent
from app.llm.glm_client import glm_client


class BaseAgent(ABC):
    def __init__(
        self,
        id: str,
        name: str,
        agent_type: AgentType,
        description: Optional[str] = None,
        custom_prompt: Optional[str] = None,
        position: Optional[Dict[str, float]] = None,
    ):
        self.id = id
        self.name = name
        self.type = agent_type
        self.description = description
        self.custom_prompt = custom_prompt
        self.status = AgentStatus.IDLE
        self.position = position or {"x": 0, "y": 0, "z": 0}
        self.current_task_id: Optional[str] = None
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value,
            "description": self.description,
            "custom_prompt": self.custom_prompt,
            "status": self.status.value,
            "position": self.position,
            "current_task_id": self.current_task_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    def update_status(self, status: AgentStatus):
        self.status = status
        self.updated_at = datetime.utcnow()

    def set_position(self, x: float, y: float, z: float):
        self.position = {"x": x, "y": y, "z": z}
        self.updated_at = datetime.utcnow()

    @abstractmethod
    async def execute_task(self, task: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Execute a task and yield progress updates"""
        pass

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Get the system prompt for this agent type"""
        pass


class CoderAgent(BaseAgent):
    def __init__(self, id: str, name: str, **kwargs):
        super().__init__(id, name, AgentType.CODER, **kwargs)

    def get_system_prompt(self) -> str:
        return self.custom_prompt or """你是一个专业的代码开发专家。你的职责包括：
1. 编写高质量、可维护的代码
2. 调试和修复代码问题
3. 进行代码审查和优化
4. 解释技术概念和最佳实践

请用专业但友好的方式回应，必要时提供代码示例。"""

    async def execute_task(self, task: str) -> AsyncGenerator[Dict[str, Any], None]:
        self.update_status(AgentStatus.WORKING)

        yield {"type": "thinking", "content": f"[{self.name}] 开始分析代码任务..."}
        yield {"type": "thinking", "content": f"[{self.name}] 理解需求：{task}"}

        async for chunk in glm_client.chat_stream(task, "coder", self.custom_prompt):
            yield {"type": "stream", "content": chunk}

        self.update_status(AgentStatus.IDLE)
        yield {"type": "complete", "content": "任务完成"}


class AnalystAgent(BaseAgent):
    def __init__(self, id: str, name: str, **kwargs):
        super().__init__(id, name, AgentType.ANALYST, **kwargs)

    def get_system_prompt(self) -> str:
        return self.custom_prompt or """你是一个专业的数据分析师。你的职责包括：
1. 分析数据并提供洞察
2. 生成分析报告
3. 创建数据可视化建议
4. 解读数据趋势和模式

请用清晰、结构化的方式呈现分析结果。"""

    async def execute_task(self, task: str) -> AsyncGenerator[Dict[str, Any], None]:
        self.update_status(AgentStatus.WORKING)

        yield {"type": "thinking", "content": f"[{self.name}] 开始数据分析..."}
        yield {"type": "thinking", "content": f"[{self.name}] 分析目标：{task}"}

        async for chunk in glm_client.chat_stream(task, "analyst", self.custom_prompt):
            yield {"type": "stream", "content": chunk}

        self.update_status(AgentStatus.IDLE)
        yield {"type": "complete", "content": "分析完成"}


class AssistantAgent(BaseAgent):
    def __init__(self, id: str, name: str, **kwargs):
        super().__init__(id, name, AgentType.ASSISTANT, **kwargs)

    def get_system_prompt(self) -> str:
        return self.custom_prompt or """你是一个智能通用助手。你的职责包括：
1. 回答各种问题
2. 提供建议和解决方案
3. 协助完成各种任务
4. 进行友好对话

请用友好、专业的方式回应。"""

    async def execute_task(self, task: str) -> AsyncGenerator[Dict[str, Any], None]:
        self.update_status(AgentStatus.WORKING)

        yield {"type": "thinking", "content": f"[{self.name}] 处理请求..."}
        yield {"type": "thinking", "content": f"[{self.name}] 任务内容：{task}"}

        async for chunk in glm_client.chat_stream(task, "assistant", self.custom_prompt):
            yield {"type": "stream", "content": chunk}

        self.update_status(AgentStatus.IDLE)
        yield {"type": "complete", "content": "处理完成"}


class CustomAgent(BaseAgent):
    def __init__(self, id: str, name: str, custom_prompt: str, **kwargs):
        super().__init__(id, name, AgentType.CUSTOM, custom_prompt=custom_prompt, **kwargs)

    def get_system_prompt(self) -> str:
        return self.custom_prompt or "你是一个自定义AI助手。"

    async def execute_task(self, task: str) -> AsyncGenerator[Dict[str, Any], None]:
        self.update_status(AgentStatus.WORKING)

        yield {"type": "thinking", "content": f"[{self.name}] 开始处理自定义任务..."}
        yield {"type": "thinking", "content": f"[{self.name}] 任务：{task}"}

        async for chunk in glm_client.chat_stream(task, "custom", self.custom_prompt):
            yield {"type": "stream", "content": chunk}

        self.update_status(AgentStatus.IDLE)
        yield {"type": "complete", "content": "任务完成"}


def create_agent(
    name: str,
    agent_type: AgentType,
    description: Optional[str] = None,
    custom_prompt: Optional[str] = None,
    position: Optional[Dict[str, float]] = None,
) -> BaseAgent:
    """Factory function to create agents"""
    agent_id = str(uuid.uuid4())

    if agent_type == AgentType.CODER:
        return CoderAgent(agent_id, name, description=description, custom_prompt=custom_prompt, position=position)
    elif agent_type == AgentType.ANALYST:
        return AnalystAgent(agent_id, name, description=description, custom_prompt=custom_prompt, position=position)
    elif agent_type == AgentType.ASSISTANT:
        return AssistantAgent(agent_id, name, description=description, custom_prompt=custom_prompt, position=position)
    elif agent_type == AgentType.CUSTOM:
        return CustomAgent(agent_id, name, custom_prompt=custom_prompt or "", description=description, position=position)
    else:
        return AssistantAgent(agent_id, name, description=description, custom_prompt=custom_prompt, position=position)
