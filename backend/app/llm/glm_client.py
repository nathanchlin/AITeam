from zhipuai import ZhipuAI
from typing import Optional, AsyncGenerator, List, Dict, Any
import json
import asyncio
import threading
from app.config import settings


class GLMClient:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.glm_api_key
        self.model = model or settings.glm_model
        self.client = ZhipuAI(api_key=self.api_key) if self.api_key else None

    def _get_system_prompt(self, agent_type: str, custom_prompt: Optional[str] = None) -> str:
        base_prompts = {
            "coder": """你是一个专业的代码开发助手。你的职责是：
1. 编写高质量、可维护的代码
2. 调试和修复代码问题
3. 进行代码审查和优化
4. 解释技术概念和最佳实践

请用专业但友好的方式回应，必要时提供代码示例。""",
            "analyst": """你是一个专业的数据分析师。你的职责是：
1. 分析数据并提供洞察
2. 生成分析报告
3. 创建数据可视化建议
4. 解读数据趋势和模式

请用清晰、结构化的方式呈现分析结果。""",
            "assistant": """你是一个智能通用助手。你的职责是：
1. 回答各种问题
2. 提供建议和解决方案
3. 协助完成各种任务
4. 进行友好对话

请用友好、专业的方式回应。""",
            "tester": """你是一个专业的软件测试工程师。你的职责是：
1. 分析需求并设计测试用例
2. 执行功能测试和回归测试
3. 发现并报告Bug
4. 验证Bug修复

请用系统化、严谨的方式工作。""",
            "custom": custom_prompt or "你是一个自定义AI助手。请根据用户的需求提供帮助。"
        }
        return base_prompts.get(agent_type, base_prompts["assistant"])

    async def chat(
        self,
        message: str,
        agent_type: str = "assistant",
        custom_prompt: Optional[str] = None,
        history: Optional[List[Dict[str, str]]] = None,
    ) -> str:
        if not self.client:
            return "错误：未配置 GLM API Key，请在 .env 文件中配置 GLM_API_KEY"

        system_prompt = self._get_system_prompt(agent_type, custom_prompt)
        messages = [{"role": "system", "content": system_prompt}]

        if history:
            messages.extend(history)

        messages.append({"role": "user", "content": message})

        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=messages,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"调用 GLM API 时出错：{str(e)}"

    async def chat_stream(
        self,
        message: str,
        agent_type: str = "assistant",
        custom_prompt: Optional[str] = None,
        history: Optional[List[Dict[str, str]]] = None,
    ) -> AsyncGenerator[str, None]:
        if not self.client:
            yield "错误：未配置 GLM API Key"
            return

        system_prompt = self._get_system_prompt(agent_type, custom_prompt)
        messages = [{"role": "system", "content": system_prompt}]

        if history:
            messages.extend(history)

        messages.append({"role": "user", "content": message})

        try:
            # 在线程中创建流，避免阻塞事件循环
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=messages,
                stream=True,
            )
        except Exception as e:
            yield f"[错误] {str(e)}"
            return

        # 在后台线程中消费流，通过 queue 传给异步端，这样 asyncio.wait_for 才能生效
        queue: asyncio.Queue[Optional[str]] = asyncio.Queue()
        loop = asyncio.get_event_loop()

        def consume_stream():
            try:
                for chunk in response:
                    if chunk.choices and chunk.choices[0].delta.content:
                        loop.call_soon_threadsafe(queue.put_nowait, chunk.choices[0].delta.content)
            except Exception as e:
                loop.call_soon_threadsafe(queue.put_nowait, f"[错误] {str(e)}")
            finally:
                loop.call_soon_threadsafe(queue.put_nowait, None)

        threading.Thread(target=consume_stream, daemon=True).start()

        while True:
            chunk = await queue.get()
            if chunk is None:
                break
            yield chunk

    async def think_and_act(
        self,
        task: str,
        agent_type: str = "assistant",
        custom_prompt: Optional[str] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        thinking_prompt = f"""请分析以下任务并逐步思考解决方案。对于每一步，请用JSON格式输出：

任务：{task}

请按以下格式输出（每行一个JSON）：
{{"type": "thinking", "content": "你的思考内容"}}
{{"type": "action", "content": "你要执行的动作"}}
{{"type": "result", "content": "最终结果或建议"}}

开始思考："""

        if not self.client:
            yield {"type": "error", "content": "未配置 GLM API Key"}
            return

        full_response = ""
        async for chunk in self.chat_stream(thinking_prompt, agent_type, custom_prompt):
            full_response += chunk
            yield {"type": "stream", "content": chunk}

        yield {"type": "complete", "content": full_response}


# Global instance
glm_client = GLMClient()
