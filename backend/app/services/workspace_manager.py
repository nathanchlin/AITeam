"""
Agent Workspace Manager - 为每个 Agent 管理独立的工作目录

目录结构:
backend/data/workspaces/{agent_name}/
├── IDENTITY.md          ← 人格（名字、性格、沟通风格）
├── SOUL.md              ← 角色定义（专业领域、方法论）
├── USER.md              ← 用户画像（偏好、项目背景）
├── MEMORY.md            ← 持久记忆（关键学习、模式、偏好）
└── memory/
    └── 2026-03-28.md    ← 每日日志
"""

import os
from typing import Optional, List
from datetime import datetime
from app.models.schemas import AgentType


# 模板目录
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), '..', 'templates', 'workspace_defaults')
# 工作区根目录
WORKSPACE_BASE = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'workspaces')


class WorkspaceManager:
    """管理 Agent 的独立工作目录和上下文文件"""

    def __init__(self, base_path: Optional[str] = None):
        self.base_path = base_path or WORKSPACE_BASE
        os.makedirs(self.base_path, exist_ok=True)

    def _get_workspace_path(self, agent_id: str) -> str:
        """获取 Agent workspace 目录路径"""
        return os.path.join(self.base_path, agent_id)

    def _read_file_safe(self, filepath: str) -> str:
        """安全读取文件，失败返回空字符串"""
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception as e:
            print(f"[WorkspaceManager] Error reading {filepath}: {e}")
        return ""

    def _write_file_safe(self, filepath: str, content: str) -> bool:
        """安全写入文件"""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"[WorkspaceManager] Error writing {filepath}: {e}")
            return False

    def _read_template(self, template_name: str) -> str:
        """读取模板文件"""
        filepath = os.path.join(TEMPLATE_DIR, template_name)
        return self._read_file_safe(filepath)

    def workspace_exists(self, agent_id: str) -> bool:
        """检查 workspace 是否存在"""
        return os.path.isdir(self._get_workspace_path(agent_id))

    def initialize_workspace(
        self,
        agent_id: str,
        agent_type: AgentType,
        agent_name: str,
    ) -> str:
        """为 Agent 创建 workspace 目录和默认文件

        Args:
            agent_id: Agent 唯一标识
            agent_type: Agent 类型
            agent_name: Agent 名称

        Returns:
            workspace 目录路径
        """
        ws_path = self._get_workspace_path(agent_id)

        if os.path.exists(ws_path):
            return ws_path

        os.makedirs(ws_path, exist_ok=True)
        os.makedirs(os.path.join(ws_path, 'memory'), exist_ok=True)

        # 确定类型前缀（coder, analyst, assistant, tester, custom）
        type_prefix = self._get_type_prefix(agent_type)

        # 创建 IDENTITY.md
        identity_template = self._read_template(f"{type_prefix}_identity.md")
        if not identity_template:
            identity_template = f"# {agent_name}\n\n你是 {agent_name}，一个 AI 助手。\n"
        identity_content = identity_template.replace("{{name}}", agent_name)
        self._write_file_safe(os.path.join(ws_path, "IDENTITY.md"), identity_content)

        # 创建 SOUL.md
        soul_template = self._read_template(f"{type_prefix}_soul.md")
        if not soul_template:
            soul_template = "# 角色定义\n\n你是一个专业的 AI 助手。\n"
        soul_content = soul_template.replace("{{name}}", agent_name)
        self._write_file_safe(os.path.join(ws_path, "SOUL.md"), soul_content)

        # 创建 USER.md
        user_content = "# 用户画像\n\n## 偏好\n- 使用中文沟通\n- 喜欢简洁清晰的回复\n\n## 项目背景\n- AITeam 多 Agent 协作系统\n"
        self._write_file_safe(os.path.join(ws_path, "USER.md"), user_content)

        # 创建 MEMORY.md
        memory_content = f"# 持久记忆\n\n> 创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n## 关键学习\n\n（暂无记录）\n\n## 常见模式\n\n（暂无记录）\n"
        self._write_file_safe(os.path.join(ws_path, "MEMORY.md"), memory_content)

        print(f"[WorkspaceManager] Initialized workspace for {agent_name} ({agent_type.value}) at {ws_path}")
        return ws_path

    def _get_type_prefix(self, agent_type: AgentType) -> str:
        """将 AgentType 映射为模板文件前缀"""
        mapping = {
            AgentType.CODER: "coder",
            AgentType.PUA_CODER: "coder",
            AgentType.ANALYST: "analyst",
            AgentType.PUA_ANALYST: "analyst",
            AgentType.ASSISTANT: "assistant",
            AgentType.PUA_ASSISTANT: "assistant",
            AgentType.TESTER: "tester",
            AgentType.PUA_TESTER: "tester",
            AgentType.CUSTOM: "assistant",
        }
        return mapping.get(agent_type, "assistant")

    def load_workspace_context(
        self,
        agent_id: str,
        max_chars: int = 8000,
    ) -> str:
        """加载 workspace 文件并格式化为可注入 prompt 的上下文

        Args:
            agent_id: Agent ID
            max_chars: 最大字符数限制

        Returns:
            格式化的 workspace 上下文字符串，如果不存在返回空字符串
        """
        ws_path = self._get_workspace_path(agent_id)
        if not os.path.isdir(ws_path):
            return ""

        sections = []
        total_chars = 0

        # 按优先级加载：SOUL > MEMORY > IDENTITY > USER
        file_order = [
            ("SOUL.md", "=== 角色定义 ==="),
            ("MEMORY.md", "=== 持久记忆 ==="),
            ("IDENTITY.md", "=== 身份信息 ==="),
            ("USER.md", "=== 用户画像 ==="),
        ]

        for filename, header in file_order:
            filepath = os.path.join(ws_path, filename)
            content = self._read_file_safe(filepath)
            if not content.strip():
                continue

            section = f"\n{header}\n{content}"
            if total_chars + len(section) > max_chars:
                # 截断此部分
                remaining = max_chars - total_chars
                if remaining > 100:
                    content = content[:remaining - 50] + "\n...（已截断）"
                    section = f"\n{header}\n{content}"
                    sections.append(section)
                break

            sections.append(section)
            total_chars += len(section)

        return "".join(sections)

    def update_memory(
        self,
        agent_id: str,
        task_summary: str,
        learnings: List[str],
        outcome: str,
    ) -> None:
        """更新 Agent 的 MEMORY.md

        Args:
            agent_id: Agent ID
            task_summary: 任务摘要
            learnings: 学习点列表
            outcome: 结果 (success/failed/timeout)
        """
        ws_path = self._get_workspace_path(agent_id)
        memory_path = os.path.join(ws_path, "MEMORY.md")

        existing = self._read_file_safe(memory_path)

        # 构建新条目
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        outcome_emoji = "✅" if outcome == "success" else "❌"
        entry = f"\n### {timestamp} - {outcome_emoji} {outcome}\n**任务**: {task_summary}\n"

        if learnings:
            entry += "**学习点**:\n"
            for learning in learnings[:5]:  # 最多5个学习点
                entry += f"- {learning}\n"

        # 在 "关键学习" 部分后追加
        if "（暂无记录）" in existing:
            existing = existing.replace("（暂无记录）", entry)
        else:
            # 在 "常见模式" 之前插入
            if "## 常见模式" in existing:
                existing = existing.replace("## 常见模式", entry + "\n## 常见模式")
            else:
                existing += entry

        # 裁剪过长的内容（保留最近的记录）
        existing = self._trim_content(existing, max_chars=10000)

        self._write_file_safe(memory_path, existing)

    def update_daily_log(self, agent_id: str, entry: str) -> None:
        """更新每日日志

        Args:
            agent_id: Agent ID
            entry: 日志条目
        """
        ws_path = self._get_workspace_path(agent_id)
        memory_dir = os.path.join(ws_path, "memory")
        os.makedirs(memory_dir, exist_ok=True)

        today = datetime.now().strftime('%Y-%m-%d')
        log_path = os.path.join(memory_dir, f"{today}.md")

        existing = self._read_file_safe(log_path)

        timestamp = datetime.now().strftime('%H:%M')
        new_line = f"- **{timestamp}** {entry}\n"

        if not existing:
            header = f"# 日志 {today}\n\n"
            existing = header + new_line
        else:
            existing += new_line

        self._write_file_safe(log_path, existing)

    def get_workspace_files(self, agent_id: str) -> dict:
        """获取 workspace 所有文件内容（用于 API 返回）"""
        ws_path = self._get_workspace_path(agent_id)
        if not os.path.isdir(ws_path):
            return {}

        result = {}
        for filename in ["IDENTITY.md", "SOUL.md", "USER.md", "MEMORY.md"]:
            filepath = os.path.join(ws_path, filename)
            result[filename] = self._read_file_safe(filepath)

        # 加载每日日志（最近5天）
        memory_dir = os.path.join(ws_path, "memory")
        if os.path.isdir(memory_dir):
            log_files = sorted(
                [f for f in os.listdir(memory_dir) if f.endswith('.md')],
                reverse=True,
            )[:5]
            result["daily_logs"] = []
            for lf in log_files:
                content = self._read_file_safe(os.path.join(memory_dir, lf))
                result["daily_logs"].append({"date": lf.replace('.md', ''), "content": content})

        return result

    def update_workspace_file(
        self,
        agent_id: str,
        filename: str,
        content: str,
    ) -> bool:
        """更新 workspace 中的指定文件"""
        # 安全检查：只允许更新白名单文件
        allowed_files = {"IDENTITY.md", "SOUL.md", "USER.md", "MEMORY.md"}
        if filename not in allowed_files:
            return False

        ws_path = self._get_workspace_path(agent_id)
        if not os.path.isdir(ws_path):
            return False

        filepath = os.path.join(ws_path, filename)
        return self._write_file_safe(filepath, content)

    def _trim_content(self, content: str, max_chars: int = 10000) -> str:
        """裁剪过长的内容，保留头部和最近的条目"""
        if len(content) <= max_chars:
            return content

        # 保留头部（到第一个 ### 之前）
        header_end = content.find("###")
        if header_end == -1:
            return content[:max_chars]

        header = content[:header_end]

        # 从尾部保留最近的记录
        entries = content[header_end:].split("### ")
        # 保留最近的条目
        while entries and len(header) + sum(len("### " + e) for e in entries) > max_chars:
            entries.pop(0)

        return header + "### ".join(entries)


# 全局实例
workspace_manager = WorkspaceManager()
