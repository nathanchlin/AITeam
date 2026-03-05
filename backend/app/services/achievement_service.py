"""
成就系统服务

负责检查和授予 agent 成就，包括：
- 加载成就定义
- 检查成就条件
- 授予成就并广播
"""
import json
import os
from typing import Dict, List, Any, Optional
from pathlib import Path

from app.api.ws import ws_manager as websocket_manager


class AchievementService:
    """成就系统服务"""

    def __init__(self, data_dir: str = "app/data"):
        self.data_dir = Path(data_dir)
        self.achievements_file = self.data_dir / "achievements.json"
        self.achievements: Dict[str, Dict[str, Any]] = {}
        self._load_achievements()

    def _load_achievements(self) -> None:
        """加载成就定义"""
        try:
            if self.achievements_file.exists():
                with open(self.achievements_file, "r", encoding="utf-8") as f:
                    self.achievements = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Failed to load achievements: {e}")
            self.achievements = {}

    def reload_achievements(self) -> None:
        """重新加载成就定义"""
        self._load_achievements()

    def get_all_achievements(self) -> Dict[str, Dict[str, Any]]:
        """获取所有成就定义"""
        return self.achievements

    def get_achievement(self, achievement_id: str) -> Optional[Dict[str, Any]]:
        """获取单个成就定义"""
        return self.achievements.get(achievement_id)

    def check_achievements(
        self,
        agent_id: str,
        stats: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        检查成就是否达成

        Args:
            agent_id: Agent ID
            stats: Agent 的统计数据，包括：
                - tasks_completed: 完成任务数
                - tasks_successful: 成功任务数
                - level: 当前等级
                - quality_streak: 质量连胜数
                - pipeline_count: 参与 Pipeline 次数
            context: 临时上下文信息，如：
                - quality_grade: 本次质量评分
                - success: 本次是否成功

        Returns:
            新解锁的成就列表
        """
        if context is None:
            context = {}

        unlocked_achievements = []

        for achievement_id, achievement in self.achievements.items():
            condition = achievement.get("condition", {})

            if self._check_condition(condition, stats, context):
                if self.grant_achievement(agent_id, achievement_id):
                    unlocked_achievements.append(achievement)

        return unlocked_achievements

    def _check_condition(
        self,
        condition: Dict[str, Any],
        stats: Dict[str, Any],
        context: Dict[str, Any]
    ) -> bool:
        """检查单个成就条件"""
        for key, value in condition.items():
            # 检查统计数据
            if key in stats:
                if isinstance(value, int):
                    if stats[key] < value:
                        return False
                elif isinstance(value, bool):
                    if bool(stats[key]) != value:
                        return False
                elif stats[key] != value:
                    return False
            # 检查上下文信息（如单次质量评分）
            elif key in context:
                if context[key] != value:
                    return False
            else:
                return False

        return True

    def grant_achievement(self, agent_id: str, achievement_id: str) -> bool:
        """
        授予成就

        Args:
            agent_id: Agent ID
            achievement_id: 成就 ID

        Returns:
            True 如果是新成就，False 如果已获得
        """
        # 获取 agent 的已获得成就列表
        agents_file = self.data_dir / "agents.json"
        agent_achievements = []

        try:
            if agents_file.exists():
                with open(agents_file, "r", encoding="utf-8") as f:
                    agents_data = json.load(f)

                if agent_id in agents_data:
                    agent_data = agents_data[agent_id]
                    agent_achievements = agent_data.get("achievements", [])

            # 检查是否已获得
            if achievement_id in agent_achievements:
                return False

            # 添加新成就
            agent_achievements.append(achievement_id)

            # 获取成就定义
            achievement = self.achievements.get(achievement_id, {})
            xp_reward = achievement.get("xp_reward", 0)

            # 更新 agent 数据
            if agents_file.exists():
                with open(agents_file, "r", encoding="utf-8") as f:
                    agents_data = json.load(f)

                if agent_id in agents_data:
                    # 增加 XP
                    current_xp = agents_data[agent_id].get("xp", 0)
                    agents_data[agent_id]["xp"] = current_xp + xp_reward
                    agents_data[agent_id]["achievements"] = agent_achievements

                    with open(agents_file, "w", encoding="utf-8") as f:
                        json.dump(agents_data, f, indent=2, ensure_ascii=False)

            # 广播成就解锁消息
            self._broadcast_achievement_unlocked(agent_id, achievement)

            return True

        except (json.JSONDecodeError, IOError) as e:
            print(f"Failed to grant achievement: {e}")
            return False

    def _broadcast_achievement_unlocked(
        self,
        agent_id: str,
        achievement: Dict[str, Any]
    ) -> None:
        """广播成就解锁消息"""
        message = {
            "type": "achievement_unlocked",
            "data": {
                "agent_id": agent_id,
                "achievement_id": achievement.get("id"),
                "achievement_name": achievement.get("name"),
                "description": achievement.get("description"),
                "icon": achievement.get("icon"),
                "xp_reward": achievement.get("xp_reward", 0)
            }
        }

        try:
            import asyncio
            asyncio.create_task(websocket_manager.broadcast(message))
        except Exception as e:
            print(f"Failed to broadcast achievement: {e}")

    def get_agent_achievements(self, agent_id: str) -> List[Dict[str, Any]]:
        """
        获取 agent 的已获得成就

        Args:
            agent_id: Agent ID

        Returns:
            已获得的成就详情列表
        """
        agents_file = self.data_dir / "agents.json"

        try:
            if agents_file.exists():
                with open(agents_file, "r", encoding="utf-8") as f:
                    agents_data = json.load(f)

                if agent_id in agents_data:
                    agent_achievements = agents_data[agent_id].get("achievements", [])
                    return [
                        self.achievements.get(aid, {})
                        for aid in agent_achievements
                        if aid in self.achievements
                    ]
        except (json.JSONDecodeError, IOError) as e:
            print(f"Failed to get agent achievements: {e}")

        return []

    def get_achievement_progress(
        self,
        agent_id: str,
        stats: Dict[str, Any]
    ) -> Dict[str, Dict[str, Any]]:
        """
        获取成就进度

        Args:
            agent_id: Agent ID
            stats: Agent 统计数据

        Returns:
            成就进度字典，包含当前值和目标值
        """
        progress = {}
        agent_achievements = []

        # 获取已获得的成就
        agents_file = self.data_dir / "agents.json"
        if agents_file.exists():
            try:
                with open(agents_file, "r", encoding="utf-8") as f:
                    agents_data = json.load(f)
                if agent_id in agents_data:
                    agent_achievements = agents_data[agent_id].get("achievements", [])
            except (json.JSONDecodeError, IOError):
                pass

        for achievement_id, achievement in self.achievements.items():
            condition = achievement.get("condition", {})

            if achievement_id in agent_achievements:
                progress[achievement_id] = {"unlocked": True, "progress": 1.0}
            else:
                # 计算进度
                current = 0
                target = 0

                for key, value in condition.items():
                    if isinstance(value, int):
                        current = stats.get(key, 0)
                        target = value
                        break
                    elif isinstance(value, bool):
                        current = 1 if stats.get(key, False) else 0
                        target = 1
                        break

                progress_ratio = min(current / target, 1.0) if target > 0 else 0.0
                progress[achievement_id] = {
                    "unlocked": False,
                    "current": current,
                    "target": target,
                    "progress": progress_ratio
                }

        return progress


# 全局单例
_achievement_service: Optional[AchievementService] = None


def get_achievement_service() -> AchievementService:
    """获取成就服务单例"""
    global _achievement_service
    if _achievement_service is None:
        _achievement_service = AchievementService()
    return _achievement_service
