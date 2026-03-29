"""Tool Registry - Agent 工具注册与执行管理"""

from typing import Dict, List, Callable, Any, Optional
import json


class ToolRegistry:
    """工具注册表：管理 Agent 可用的工具定义和执行"""

    def __init__(self):
        self._tools: Dict[str, Dict[str, Any]] = {}  # name -> {schema, handler, available_to}
        self._handlers: Dict[str, Callable] = {}

    def register_tool(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        handler: Callable,
        available_to: Optional[List[str]] = None,
    ):
        """注册工具

        Args:
            name: 工具名
            description: 工具描述
            parameters: JSON Schema 格式的参数定义
            handler: 异步执行函数 async handler(**kwargs) -> str
            available_to: 可用的 agent type 列表，None 表示所有 agent 可用
        """
        self._tools[name] = {
            "schema": {
                "type": "function",
                "function": {
                    "name": name,
                    "description": description,
                    "parameters": parameters,
                }
            },
            "available_to": available_to,
        }
        self._handlers[name] = handler

    def get_tools_schema(self, agent_type: str) -> List[Dict[str, Any]]:
        """获取指定 agent 类型可用的工具 schema 列表（GLM API 格式）"""
        result = []
        for name, tool_def in self._tools.items():
            available_to = tool_def.get("available_to")
            if available_to is None or agent_type in available_to:
                result.append(tool_def["schema"])
        return result

    async def execute_tool(self, name: str, arguments: Dict[str, Any], sandbox: Dict[str, Any]) -> str:
        """执行工具调用

        Args:
            name: 工具名
            arguments: 工具参数
            sandbox: 沙箱上下文（如 workspace_path）

        Returns:
            工具执行结果字符串
        """
        handler = self._handlers.get(name)
        if not handler:
            return f"错误：未知工具 '{name}'"

        try:
            result = await handler(**arguments, _sandbox=sandbox)
            # 截断过长的结果
            if len(result) > 4000:
                result = result[:3800] + "\n...（结果已截断）"
            return result
        except Exception as e:
            return f"工具执行错误 ({name}): {str(e)}"

    def list_tools(self) -> List[str]:
        """列出所有已注册的工具名"""
        return list(self._tools.keys())

    def has_tools(self, agent_type: str) -> bool:
        """检查指定 agent 类型是否有可用工具"""
        return len(self.get_tools_schema(agent_type)) > 0


# 全局工具注册表
tool_registry = ToolRegistry()
