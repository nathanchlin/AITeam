from typing import Tuple, Optional
from datetime import datetime
import random


class MotivationService:
    """动机/情感系统服务"""

    # 动机变化规则
    MOTIVATION_CHANGES = {
        "task_completed": 0.1,
        "perfect_success": 0.2,  # 无重试成功
        "quality_a": 0.3,
        "achievement_unlocked": 0.2,
        "task_failed": -0.2,
        "decay_hourly": -0.05
    }

    # 情感状态阈值
    EMOTION_STATES = {
        "excited": {"threshold": 0.8, "emoji": "🔥", "label": "兴奋"},
        "happy": {"threshold": 0.6, "emoji": "😊", "label": "开心"},
        "calm": {"threshold": 0.4, "emoji": "😐", "label": "平静"},
        "bored": {"threshold": 0.2, "emoji": "😑", "label": "无聊"},
        "frustrated": {"threshold": 0.0, "emoji": "😢", "label": "沮丧"}
    }

    # 回复前缀
    MOTIVATION_PREFIXES = {
        "excited": ["太棒了！", "这个任务很有趣！", "让我来搞定它！"],
        "happy": ["好的！", "没问题！", "开始吧！"],
        "calm": ["好的，我会完成这个任务。", "明白了。"],
        "bored": ["嗯...我会尽力完成。", "好的，开始吧..."],
        "frustrated": ["我会尝试完成...", "让我试试看..."]
    }

    def __init__(self):
        pass

    def clamp_motivation(self, value: float) -> float:
        """限制动机值在 0.2-1.0 范围内

        Args:
            value: 原始动机值

        Returns:
            限制后的动机值（0.2-1.0）
        """
        return max(0.2, min(1.0, value))

    def apply_decay(self, stats: dict) -> float:
        """应用动机衰减

        Args:
            stats: Agent 统计信息字典，包含 last_motivation_decay

        Returns:
            应用衰减后的动机值变化量
        """
        last_decay = stats.get("last_motivation_decay")
        if last_decay is None:
            stats["last_motivation_decay"] = datetime.now()
            return 0.0

        last_decay_time = last_decay if isinstance(last_decay, datetime) else datetime.fromisoformat(last_decay)
        time_diff = datetime.now() - last_decay_time

        # 计算小时数并应用衰减
        hours_passed = time_diff.total_seconds() / 3600
        decay_amount = hours_passed * self.MOTIVATION_CHANGES["decay_hourly"]

        # 更新最后衰减时间
        stats["last_motivation_decay"] = datetime.now()

        return decay_amount

    def get_emotion_state(self, motivation: float) -> Tuple[str, str, str]:
        """根据动机值获取情感状态

        Args:
            motivation: 当前动机值（0.2-1.0）

        Returns:
            (state_key, emoji, label) 情感状态元组
        """
        # 按阈值从高到低检查
        for state_key, state_info in self.EMOTION_STATES.items():
            if motivation >= state_info["threshold"]:
                return (
                    state_key,
                    state_info["emoji"],
                    state_info["label"]
                )

        # 如果都低于阈值，返回最低状态
        return "frustrated", self.EMOTION_STATES["frustrated"]["emoji"], self.EMOTION_STATES["frustrated"]["label"]

    def get_motivation_prefix(self, motivation: float) -> str:
        """根据动机值获取随机回复前缀

        Args:
            motivation: 当前动机值（0.2-1.0）

        Returns:
            随机选择的回复前缀字符串
        """
        emotion_state, _, _ = self.get_emotion_state(motivation)
        prefixes = self.MOTIVATION_PREFIXES.get(emotion_state, ["好的，"])
        return random.choice(prefixes)

    def update_motivation(
        self,
        agent_id: str,
        event_type: str,
        stats: dict,
        extra_data: Optional[dict] = None
    ) -> float:
        """更新代理的动机值

        Args:
            agent_id: 代理 ID
            event_type: 事件类型（task_completed, perfect_success, quality_a, achievement_unlocked, task_failed）
            stats: Agent 统计信息字典，会更新其中的 motivation 和相关字段
            extra_data: 额外数据，如重试次数等

        Returns:
            更新后的动机值
        """
        # 首先应用衰减
        current_motivation = stats.get("motivation", 1.0)
        decay_amount = self.apply_decay(stats)
        current_motivation = self.clamp_motivation(current_motivation + decay_amount)

        # 获取事件对应的动机变化量
        change = self.MOTIVATION_CHANGES.get(event_type, 0.0)

        # 特殊逻辑：perfect_success 需要 extra_data 判断是否无重试
        if event_type == "perfect_success" and extra_data:
            retry_count = extra_data.get("retry_count", 0)
            if retry_count > 0:
                # 有重试，不算完美成功
                change = 0.0

        # 应用变化
        current_motivation = self.clamp_motivation(current_motivation + change)
        stats["motivation"] = current_motivation

        # 记录最后一次事件类型和时间
        stats["last_event_type"] = event_type
        stats["last_event_time"] = datetime.now()

        return current_motivation


# 创建全局实例
motivation_service = MotivationService()
