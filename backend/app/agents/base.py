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

⚠️🚨 严格规则 - 违反将导致代码无法运行：

【禁止事项 - 绝对不可】
❌ 禁止引用外部文件：<link href="css/xxx">, <script src="js/xxx">
❌ 禁止重复定义同一个类：class Game {} 只能定义一次
❌ 禁止混用多个框架：选择一种实现方式（Canvas 或 Phaser），不要两者混用
❌ 禁止使用未定义的类/函数：使用前必须先完整定义
❌ 禁止依赖未引入的库：如果用 Phaser 必须 <script src="phaser.js">
❌ 禁止引用不存在的 DOM 元素：getElementById 必须对应真实元素

【必须遵守 - 强制要求】
✅ 所有代码必须是单个完整的 HTML 文件
✅ 结构规范：<!DOCTYPE html><html><head><style>CSS</style></head><body>HTML元素<script>JS</script></body></html>
✅ 所有 CSS 内联在 <style> 标签中
✅ 所有 JavaScript 内联在 <script> 标签中
✅ 每个类只定义一次，不要在多处重复定义
✅ 类必须在使用前完整定义
✅ 必须包含初始化代码：window.onload 或 DOMContentLoaded
✅ 必须包含游戏循环：requestAnimationFrame 或 setInterval
✅ 游戏必须自动启动，不能只定义类不实例化

【代码质量】
- 代码必须可以直接在浏览器打开运行
- 不要写伪代码或代码片段
- 不要留 TODO 或 "..." 占位符
- 所有函数必须有完整实现

【游戏框架选择 - 重要】
🚫 禁止使用 Phaser、Pixi.js 等外部游戏框架
✅ 只能使用原生 Canvas API (getContext('2d'))
✅ 原因：单文件HTML无法加载外部框架，框架CDN可能被墙

【Web游戏开发模板】
必须使用纯 Canvas 实现：
```html
<!DOCTYPE html>
<html>
<head><style>/* 样式 */</style></head>
<body>
<canvas id="game"></canvas>
<script>
class Game { constructor() { this.init(); } init() {} update() {} draw() {} gameLoop() { this.update(); this.draw(); requestAnimationFrame(() => this.gameLoop()); } }
window.onload = () => { new Game(); };
</script>
</body>
</html>
```

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

⚠️ 重要规则 - 测试代码时必须遵守：

【技术栈识别】
- 首先识别代码使用的技术栈（Canvas、Phaser、Three.js 等）
- 如果是纯 Canvas/WebGL 代码，不需要 Phaser 等框架
- 只有代码中明确引用了某个框架，才检查该框架是否存在
- 不要假设所有游戏都需要 Phaser 或其他框架

【Canvas 游戏测试标准】
- 检查是否有 canvas 元素和 getContext('2d')
- 检查是否有游戏循环 (requestAnimationFrame 或 setInterval)
- 检查是否有初始化代码 (init 函数或 window.onload)
- 检查类和函数是否在使用前定义
- 检查事件监听是否设置

【不要误报的问题】
❌ 不要报告"缺少 Phaser.js"如果代码使用纯 Canvas
❌ 不要报告"缺少外部文件"如果代码是完整的单文件
❌ 不要要求未使用的技术栈

【真正的代码问题】
✅ 使用了未定义的变量或函数
✅ 缺少必要的初始化代码
✅ 游戏循环没有启动
✅ 事件监听未绑定
✅ 逻辑错误或边界条件未处理

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
