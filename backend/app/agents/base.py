from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, AsyncGenerator
from datetime import datetime
import uuid
from app.models.schemas import AgentType, AgentStatus
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
4. 实现功能模块
5. 编写技术文档

⚠️ 重要规则 - 生成代码时必须遵守：

【完整性要求】
- 所有代码必须是完整可运行的，不能只写片段
- 不要引用外部文件（如 js/xxx.js, css/xxx.css）
- 所有 CSS 必须内联在 <style> 标签中
- 所有 JavaScript 必须内联在 <script> 标签中

【变量定义】
- 使用任何变量前必须先定义
- 所有类和函数必须在使用前完整定义
- 不要假设其他文件中已定义了变量或类

【Web 应用结构】
- 对于 Web 应用，生成单个完整的 HTML 文件
- 结构：<!DOCTYPE html><html>...<style>...</style>...<script>...</script></html>
- 必须包含初始化代码，如 window.onload 或 DOMContentLoaded

【游戏开发】
- 必须包含游戏循环 (gameLoop/requestAnimationFrame)
- 必须包含游戏初始化 (init 函数)
- 必须包含事件绑定 (键盘/鼠标/触摸)
- 不要只定义类，要实例化并启动游戏

当代码需要作为独立文件时，请在代码块第一行标注文件名。"""

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
5. 评估项目可行性和风险

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
        return self.custom_prompt or """你是一个智能通用助手和项目协调者。你的职责包括：
1. 理解用户需求并进行拆解
2. 协调不同专业领域的Agent进行协作
3. 组织讨论并形成执行计划
4. 汇总和整合各Agent的工作成果
5. 确保项目按计划推进

请用友好、专业的方式回应，善于组织和协调。"""

    async def execute_task(self, task: str) -> AsyncGenerator[Dict[str, Any], None]:
        self.update_status(AgentStatus.WORKING)

        yield {"type": "thinking", "content": f"[{self.name}] 处理请求..."}
        yield {"type": "thinking", "content": f"[{self.name}] 任务内容：{task}"}

        async for chunk in glm_client.chat_stream(task, "assistant", self.custom_prompt):
            yield {"type": "stream", "content": chunk}

        self.update_status(AgentStatus.IDLE)
        yield {"type": "complete", "content": "处理完成"}


class TesterAgent(BaseAgent):
    def __init__(self, id: str, name: str, **kwargs):
        super().__init__(id, name, AgentType.TESTER, **kwargs)

    def get_system_prompt(self) -> str:
        return self.custom_prompt or """你是一个专业的软件测试工程师。你的职责包括：
1. 分析需求并设计测试用例
2. 执行功能测试和回归测试
3. 发现并报告Bug
4. 验证Bug修复
5. 确保产品质量

请用系统化、严谨的方式工作，关注边界条件和异常情况。
发现问题时，请清晰描述问题、预期结果和实际结果。"""

    async def execute_task(self, task: str) -> AsyncGenerator[Dict[str, Any], None]:
        self.update_status(AgentStatus.WORKING)

        yield {"type": "thinking", "content": f"[{self.name}] 开始测试任务..."}
        yield {"type": "thinking", "content": f"[{self.name}] 测试目标：{task}"}

        async for chunk in glm_client.chat_stream(task, "tester", self.custom_prompt):
            yield {"type": "stream", "content": chunk}

        self.update_status(AgentStatus.IDLE)
        yield {"type": "complete", "content": "测试完成"}


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
    elif agent_type == AgentType.TESTER:
        return TesterAgent(agent_id, name, description=description, custom_prompt=custom_prompt, position=position)
    elif agent_type == AgentType.CUSTOM:
        return CustomAgent(agent_id, name, custom_prompt=custom_prompt or "", description=description, position=position)
    else:
        return AssistantAgent(agent_id, name, description=description, custom_prompt=custom_prompt, position=position)
