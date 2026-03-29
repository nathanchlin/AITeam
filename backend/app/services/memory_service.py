"""
记忆服务 - Agent 经验积累与自我进化

职责:
1. 从任务结果中提取学习点
2. 生成 Few-shot 示例注入 prompt
3. Prompt 自优化建议
4. 错误模式警告
"""

import os
import re
import json
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from app.services.workspace_manager import workspace_manager


class MemoryService:
    """Agent 记忆管理服务"""

    def __init__(self):
        self._feedback_store = None

    def _get_feedback_store(self):
        """延迟加载 feedback_store"""
        if self._feedback_store is None:
            try:
                from app.services.feedback_store import feedback_store
                self._feedback_store = feedback_store
            except Exception:
                pass
        return self._feedback_store

    def extract_learnings(
        self,
        task: str,
        response: str,
        outcome: str,
    ) -> List[str]:
        """从任务结果中提取学习点

        Args:
            task: 任务描述
            response: LLM 完整响应
            outcome: 结果类型 (success/failed/timeout)

        Returns:
            学习点列表
        """
        learnings = []

        if outcome == "success":
            # 成功任务：提取关键技术决策
            # 查找 "使用"、"采用"、"通过" 等关键词
            patterns = [
                r'(?:使用|采用|通过|利用)\s*(\S+?)(?:实现|完成|解决)',
                r'(?:选择|决定)\s*(.+?)(?:作为|来|方案)',
            ]
            for pattern in patterns:
                matches = re.findall(pattern, response)
                for match in matches[:2]:
                    learning = f"成功策略: {match.strip()}"
                    if learning not in learnings:
                        learnings.append(learning)

            # 提取关键模式（如"确保"、"必须"）
            must_patterns = re.findall(r'(?:确保|必须|注意|重要)[：:]\s*(.+?)(?:\n|$)', response)
            for p in must_patterns[:3]:
                learnings.append(f"经验: {p.strip()}")

        elif outcome in ("failed", "timeout"):
            # 失败任务：从 feedback_store 获取错误模式
            fb_store = self._get_feedback_store()
            if fb_store:
                guidance = fb_store.get_guidance_for_task(task)
                if guidance:
                    learnings.append(f"失败教训: {guidance[:200]}")

            # 提取错误信息
            error_patterns = re.findall(r'(?:错误|Error|失败|问题)[：:]\s*(.+?)(?:\n|$)', response, re.IGNORECASE)
            for ep in error_patterns[:2]:
                learnings.append(f"错误模式: {ep.strip()}")

        if not learnings:
            # 通用学习点
            task_type = self._classify_task(task)
            learnings.append(f"完成 {task_type} 类任务")

        return learnings[:5]

    def _classify_task(self, task: str) -> str:
        """简单任务分类"""
        import re as _re
        task_lower = task.lower()
        if any(kw in task_lower for kw in ['game', '游戏', 'canvas', '动画']):
            return "游戏开发"
        # More specific checks first (API before Web to avoid "REST api" matching Web)
        if _re.search(r'(?:api|接口|后端|rest|endpoint)', task_lower):
            return "后端开发"
        if _re.search(r'(?:test|测试|bug|检查)', task_lower):
            return "测试"
        if _re.search(r'(?:html|web|页面|ui)', task_lower):
            return "Web开发"
        return "通用"

    def build_few_shot_context(
        self,
        agent_id: str,
        task: str,
        max_examples: int = 3,
    ) -> str:
        """从 agent 记忆中构建 Few-shot 示例上下文

        Args:
            agent_id: Agent ID
            task: 当前任务描述
            max_examples: 最大示例数

        Returns:
            Few-shot 上下文字符串，如果无匹配返回空字符串
        """
        ws_path = workspace_manager._get_workspace_path(agent_id)
        memory_dir = os.path.join(ws_path, "memory")
        if not os.path.isdir(memory_dir):
            return ""

        # 读取近期日志
        examples = []
        log_files = sorted(
            [f for f in os.listdir(memory_dir) if f.endswith('.md')],
            reverse=True,
        )

        task_keywords = set(re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z]+', task.lower()))

        for lf in log_files[:14]:  # 最近14天
            filepath = os.path.join(memory_dir, lf)
            content = workspace_manager._read_file_safe(filepath)
            if not content:
                continue

            # 解析日志条目
            entries = re.findall(r'-\s*\*\*\d{2}:\d{2}\*\*\s*(.+?)(?:\n|$)', content)
            for entry in entries:
                # 检查与当前任务的关键词重叠度
                entry_words = set(re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z]+', entry.lower()))
                overlap = len(task_keywords & entry_words)
                if overlap >= 1:
                    date_str = lf.replace('.md', '')
                    examples.append({
                        "date": date_str,
                        "entry": entry.strip(),
                        "relevance": overlap,
                    })

        if not examples:
            return ""

        # 按相关性排序，取 top-N
        examples.sort(key=lambda x: x["relevance"], reverse=True)
        examples = examples[:max_examples]

        # 构建上下文
        lines = ["\n[相关经验参考]"]
        for ex in examples:
            lines.append(f"- ({ex['date']}) {ex['entry']}")

        return "\n".join(lines)

    def get_pattern_warnings(self, agent_id: str, task: str) -> Optional[str]:
        """获取任务相关的错误模式警告

        Returns:
            警告字符串，如果无匹配返回 None
        """
        fb_store = self._get_feedback_store()
        if not fb_store:
            return None

        guidance = fb_store.get_guidance_for_task(task)
        if guidance:
            return f"\n[注意 - 历史错误模式]\n{guidance[:500]}"

        return None

    def should_trigger_prompt_optimization(self, agent_id: str) -> bool:
        """判断是否应该触发 Prompt 自优化

        规则: 每完成 5 个任务且 MEMORY.md 有足够内容时触发
        """
        ws_path = workspace_manager._get_workspace_path(agent_id)
        memory_path = os.path.join(ws_path, "MEMORY.md")
        memory_content = workspace_manager._read_file_safe(memory_path)

        # 检查是否有足够的记忆条目
        entry_count = memory_content.count("###")
        return entry_count >= 5 and entry_count % 5 == 0

    def suggest_prompt_improvements(self, agent_id: str) -> Optional[str]:
        """基于历史记忆生成 SOUL.md 改进建议

        Returns:
            改进建议字符串，如果无建议返回 None
        """
        ws_path = workspace_manager._get_workspace_path(agent_id)
        memory_content = workspace_manager._read_file_safe(os.path.join(ws_path, "MEMORY.md"))
        soul_content = workspace_manager._read_file_safe(os.path.join(ws_path, "SOUL.md"))

        if len(memory_content) < 200:
            return None

        # 提取所有成功策略和失败教训
        strategies = re.findall(r'成功策略:\s*(.+)', memory_content)
        failures = re.findall(r'失败教训:\s*(.+)', memory_content)
        errors = re.findall(r'错误模式:\s*(.+)', memory_content)

        if not strategies and not failures and not errors:
            return None

        suggestions = [f"\n> 自动优化建议 ({datetime.utcnow().strftime('%Y-%m-%d %H:%M')})"]

        if strategies:
            suggestions.append("\n## 已验证的有效策略")
            for s in strategies[:3]:
                if s not in soul_content:
                    suggestions.append(f"- {s}")

        if failures or errors:
            suggestions.append("\n## 需要避免的模式")
            for f in failures[:2]:
                suggestions.append(f"- {f}")
            for e in errors[:2]:
                suggestions.append(f"- {e}")

        result = "\n".join(suggestions)
        return result if len(result) > 100 else None


# 全局实例
memory_service = MemoryService()
