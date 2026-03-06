"""
Agent Growth Service
Handles progression, XP calculation, level-ups, and achievement tracking.
"""

import json
import logging
import math
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from app.models.agent_stats import AgentStats

logger = logging.getLogger(__name__)

# Data file path
STATS_FILE = Path(__file__).parent.parent / "data" / "agent_stats.json"


class AgentGrowthService:
    """
    Service for managing agent growth, XP, levels, and achievements.
    """

    # Score constants
    SCORE_PER_DISCUSSION = 10
    SCORE_PER_TASK = 10

    # Quality coefficients for XP calculation
    QUALITY_COEFFICIENTS = {
        "A": 3.0,
        "B": 2.0,
        "C": 1.5,
        "D": 1.0,
        "F": 0.5,
    }

    # Achievement definitions
    ACHIEVEMENTS = {
        "first_task": {
            "name": "First Steps",
            "description": "Complete your first task",
            "condition": lambda s: s.tasks_completed >= 1,
        },
        "task_master": {
            "name": "Task Master",
            "description": "Complete 10 tasks",
            "condition": lambda s: s.tasks_completed >= 10,
        },
        "perfect_streak": {
            "name": "Perfectionist",
            "description": "Complete 5 A-grade tasks in a row",
            "condition": lambda s: s.quality_streak >= 5,
        },
        "no_retries": {
            "name": "Reliable",
            "description": "Complete 5 tasks without any retries",
            "condition": lambda s: s.tasks_successful >= 5,
        },
        "pipeline_veteran": {
            "name": "Pipeline Veteran",
            "description": "Participate in 5 pipelines",
            "condition": lambda s: s.pipeline_count >= 5,
        },
        "level_5": {
            "name": "Rising Star",
            "description": "Reach level 5",
            "condition": lambda s: s.level >= 5,
        },
        "level_10": {
            "name": "Expert",
            "description": "Reach level 10",
            "condition": lambda s: s.level >= 10,
        },
        "level_25": {
            "name": "Master",
            "description": "Reach level 25",
            "condition": lambda s: s.level >= 25,
        },
    }

    def __init__(self):
        self._stats_cache: Dict[str, AgentStats] = {}
        self._load_stats()

    def _load_stats(self):
        """Load agent stats from the JSON file."""
        try:
            if STATS_FILE.exists():
                with open(STATS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for agent_id, stats_data in data.items():
                        try:
                            self._stats_cache[agent_id] = AgentStats.model_validate(stats_data)
                        except Exception as e:
                            logger.error(f"Failed to load stats for {agent_id}: {e}")
            else:
                # Initialize empty stats file
                self._save_stats()
        except Exception as e:
            logger.error(f"Failed to load agent stats: {e}")
            self._stats_cache = {}

    def _save_stats(self):
        """Save agent stats to the JSON file."""
        try:
            STATS_FILE.parent.mkdir(parents=True, exist_ok=True)
            data = {
                agent_id: stats.model_dump()
                for agent_id, stats in self._stats_cache.items()
            }
            with open(STATS_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save agent stats: {e}")

    def get_agent_stats(self, agent_id: str) -> AgentStats:
        """
        Get stats for an agent, creating a new record if it doesn't exist.

        Args:
            agent_id: The unique identifier of the agent

        Returns:
            AgentStats object for the agent
        """
        if agent_id not in self._stats_cache:
            self._stats_cache[agent_id] = AgentStats(agent_id=agent_id)
            self._save_stats()
        return self._stats_cache[agent_id]

    def calculate_token_bonus(self, total_tokens: int) -> int:
        """
        Calculate token bonus score using sqrt formula to prevent gaming.
        Formula: floor(sqrt(total_tokens / 100))

        Examples:
        - 100 tokens = 1 point
        - 1,000 tokens = 3 points
        - 10,000 tokens = 10 points
        - 100,000 tokens = 31 points

        Args:
            total_tokens: Total tokens consumed

        Returns:
            Bonus score from token usage
        """
        if total_tokens < 100:
            return 0
        return int(math.sqrt(total_tokens / 100))

    def _recalculate_scores(self, stats: AgentStats):
        """
        Recalculate all score components and total.

        Args:
            stats: AgentStats object to update
        """
        stats.discussion_score = stats.discussion_count * self.SCORE_PER_DISCUSSION
        stats.task_score = stats.tasks_completed * self.SCORE_PER_TASK
        stats.token_bonus_score = self.calculate_token_bonus(stats.total_tokens_used)
        stats.score = stats.discussion_score + stats.task_score + stats.token_bonus_score

    def add_discussion_score(self, agent_id: str, tokens_used: int = 0) -> Dict:
        """
        Add score for a discussion message.

        Args:
            agent_id: The unique identifier of the agent
            tokens_used: Tokens consumed in this discussion (optional)

        Returns:
            Dictionary with score_gained and total_score
        """
        stats = self.get_agent_stats(agent_id)
        stats.discussion_count += 1
        if tokens_used > 0:
            stats.total_tokens_used += tokens_used
        self._recalculate_scores(stats)
        stats.updated_at = datetime.now()
        self._save_stats()
        return {
            "score_gained": self.SCORE_PER_DISCUSSION,
            "total_score": stats.score,
            "discussion_count": stats.discussion_count
        }

    def add_task_score(self, agent_id: str, tokens_used: int = 0) -> Dict:
        """
        Add score for task completion. Called within on_task_completed.

        Args:
            agent_id: The unique identifier of the agent
            tokens_used: Tokens consumed in this task (optional)

        Returns:
            Dictionary with score_gained and total_score
        """
        stats = self.get_agent_stats(agent_id)
        if tokens_used > 0:
            stats.total_tokens_used += tokens_used
        self._recalculate_scores(stats)
        # Note: tasks_completed is already incremented in on_task_completed
        stats.updated_at = datetime.now()
        self._save_stats()
        return {
            "score_gained": self.SCORE_PER_TASK,
            "total_score": stats.score,
            "task_score": stats.task_score
        }

    def add_token_usage(self, agent_id: str, prompt_tokens: int = 0, completion_tokens: int = 0) -> Dict:
        """
        Record token usage for an agent.

        Args:
            agent_id: The unique identifier of the agent
            prompt_tokens: Prompt tokens used
            completion_tokens: Completion tokens used

        Returns:
            Dictionary with updated token stats
        """
        stats = self.get_agent_stats(agent_id)
        stats.prompt_tokens_used += prompt_tokens
        stats.completion_tokens_used += completion_tokens
        total = prompt_tokens + completion_tokens
        stats.total_tokens_used += total
        self._recalculate_scores(stats)
        stats.updated_at = datetime.now()
        self._save_stats()
        return {
            "total_tokens": stats.total_tokens_used,
            "token_bonus": stats.token_bonus_score,
            "score": stats.score
        }

    def calculate_xp(
        self,
        complexity: int = 1,
        quality_grade: str = "B",
        no_retries: bool = False,
    ) -> int:
        """
        Calculate XP earned for a task.

        Args:
            complexity: Task complexity (1-3)
            quality_grade: Quality grade (A, B, C, D, F)
            no_retries: Whether the task succeeded without retries

        Returns:
            XP amount earned
        """
        # Clamp complexity to valid range
        complexity = max(1, min(3, complexity))

        # Get quality coefficient
        quality_coefficient = self.QUALITY_COEFFICIENTS.get(quality_grade.upper(), 1.0)

        # Calculate base XP
        base_xp = int(complexity * quality_coefficient)

        # Apply perfect completion bonus
        perfect_bonus = 1.5 if no_retries else 1.0

        return int(base_xp * perfect_bonus)

    def add_xp(self, agent_id: str, amount: int) -> Optional[bool]:
        """
        Add XP to an agent and check for level up.

        Args:
            agent_id: The unique identifier of the agent
            amount: XP amount to add

        Returns:
            True if the agent leveled up, False otherwise, None on error
        """
        stats = self.get_agent_stats(agent_id)

        if amount <= 0:
            return None

        stats.xp += amount
        stats.updated_at = datetime.now()
        self._save_stats()

        return self.check_level_up(agent_id)

    def check_level_up(self, agent_id: str) -> bool:
        """
        Check if the agent has enough XP to level up and apply it.

        Args:
            agent_id: The unique identifier of the agent

        Returns:
            True if the agent leveled up, False otherwise
        """
        stats = self._stats_cache.get(agent_id)
        if not stats:
            return False

        leveled_up = False

        while stats.xp >= stats.xp_to_next_level and stats.level < 100:
            # Level up
            stats.xp -= stats.xp_to_next_level
            stats.level += 1

            # XP required increases by 50% each level (minimum +50)
            stats.xp_to_next_level = int(stats.xp_to_next_level * 1.5)
            stats.xp_to_next_level = max(stats.xp_to_next_level, stats.xp_to_next_level + 50)

            leveled_up = True

            # Boost motivation on level up
            stats.motivation = min(1.0, stats.motivation + 0.1)

            logger.info(f"Agent {agent_id} leveled up to level {stats.level}!")

            # Check for level achievements
            self._check_achievements(agent_id)

        if leveled_up:
            stats.updated_at = datetime.now()
            self._save_stats()

        return leveled_up

    def on_task_completed(
        self,
        agent_id: str,
        quality_grade: str = "B",
        quality_score: float = 0.7,
        retries: int = 0,
        complexity: int = 1,
    ) -> Dict:
        """
        Called when an agent completes a task successfully.

        Args:
            agent_id: The unique identifier of the agent
            quality_grade: Quality grade assigned (A, B, C, D, F)
            quality_score: Quality score (0-1)
            retries: Number of retries before success
            complexity: Task complexity (1-3)

        Returns:
            Dictionary with xp_gained and level_up status
        """
        stats = self.get_agent_stats(agent_id)

        # Update task counters
        stats.tasks_completed += 1
        if retries == 0:
            stats.tasks_successful += 1

        # Update quality streak
        if quality_grade.upper() == "A":
            stats.quality_streak += 1
        else:
            stats.quality_streak = 0

        # Recalculate scores (including task score)
        self._recalculate_scores(stats)

        # Calculate and add XP
        no_retries = retries == 0
        xp_gained = self.calculate_xp(complexity, quality_grade, no_retries)
        self.add_xp(agent_id, xp_gained)

        # Update motivation based on quality
        quality_bonus = (quality_score - 0.5) * 0.1  # Range: -0.05 to +0.05
        stats.motivation = max(0.0, min(1.0, stats.motivation + quality_bonus))
        stats.satisfaction = max(0.0, min(1.0, stats.satisfaction + quality_bonus * 0.5))

        stats.updated_at = datetime.now()

        # Check for achievements
        self._check_achievements(agent_id)

        self._save_stats()

        # Check for level up
        leveled_up = stats.xp >= stats.xp_to_next_level and stats.level < 100

        return {
            "xp_gained": xp_gained,
            "level_up": leveled_up,
            "new_level": stats.level + 1 if leveled_up else stats.level,
            "score_gained": self.SCORE_PER_TASK,
            "total_score": stats.score,
        }

    def on_task_failed(self, agent_id: str, retries: int = 0):
        """
        Called when an agent fails to complete a task.

        Args:
            agent_id: The unique identifier of the agent
            retries: Number of retries attempted
        """
        stats = self.get_agent_stats(agent_id)

        # Reset quality streak
        stats.quality_streak = 0

        # Decrease motivation (more penalty for fewer retries attempted)
        motivation_penalty = 0.05 / (retries + 1)
        stats.motivation = max(0.0, stats.motivation - motivation_penalty)

        stats.updated_at = datetime.now()
        self._save_stats()

    def on_pipeline_started(self, agent_id: str):
        """Called when an agent participates in a pipeline."""
        stats = self.get_agent_stats(agent_id)
        stats.pipeline_count += 1
        stats.motivation = min(1.0, stats.motivation + 0.02)
        stats.updated_at = datetime.now()
        self._check_achievements(agent_id)
        self._save_stats()

    def apply_motivation_decay(self, agent_id: str, hours: float = 24):
        """
        Apply motivation decay based on time since last activity.

        Args:
            agent_id: The unique identifier of the agent
            hours: Hours of inactivity before decay applies
        """
        stats = self.get_agent_stats(agent_id)

        now = datetime.now()
        last_decay = stats.last_motivation_decay or stats.created_at
        hours_since = (now - last_decay).total_seconds() / 3600

        if hours_since >= hours:
            # Decay motivation by 1% per hour of inactivity
            decay_rate = 0.01
            decay_amount = min(hours_since * decay_rate, 0.5)  # Max 50% decay
            stats.motivation = max(0.1, stats.motivation - decay_amount)
            stats.last_motivation_decay = now
            stats.updated_at = datetime.now()
            self._save_stats()

    def _check_achievements(self, agent_id: str) -> List[str]:
        """
        Check and unlock achievements for an agent.

        Args:
            agent_id: The unique identifier of the agent

        Returns:
            List of newly unlocked achievement IDs
        """
        stats = self.get_agent_stats(agent_id)
        new_achievements = []

        for achievement_id, achievement_def in self.ACHIEVEMENTS.items():
            if achievement_id not in stats.achievements:
                try:
                    if achievement_def["condition"](stats):
                        stats.achievements.append(achievement_id)
                        stats.unlocked_at[achievement_id] = datetime.now()
                        new_achievements.append(achievement_id)
                        logger.info(
                            f"Agent {agent_id} unlocked achievement: {achievement_def['name']}"
                        )
                except Exception as e:
                    logger.error(f"Error checking achievement {achievement_id}: {e}")

        if new_achievements:
            self._save_stats()

        return new_achievements

    def get_all_stats(self) -> Dict[str, Dict]:
        """
        Get all agent stats.

        Returns:
            Dictionary mapping agent_id to stats data
        """
        return {
            agent_id: stats.model_dump()
            for agent_id, stats in self._stats_cache.items()
        }

    def reset_agent_stats(self, agent_id: str):
        """
        Reset an agent's stats to initial values.

        Args:
            agent_id: The unique identifier of the agent
        """
        self._stats_cache[agent_id] = AgentStats(agent_id=agent_id)
        self._save_stats()
        logger.info(f"Reset stats for agent {agent_id}")


# Global instance
growth_service = AgentGrowthService()
