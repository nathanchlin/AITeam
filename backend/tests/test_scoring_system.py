"""
Unit tests for the Agent Scoring System
"""
import pytest
import uuid

# We'll test the scoring logic directly without database dependencies
from app.services.agent_growth_service import AgentGrowthService
from app.models.agent_stats import AgentStats
from app.llm.glm_client import TokenUsage


def unique_agent_id():
    """Generate a unique agent ID for testing"""
    return f"test-agent-{uuid.uuid4()}"


class TestScoringSystem:
    """Test the scoring system components"""

    def test_token_usage_dataclass(self):
        """Test TokenUsage dataclass"""
        usage = TokenUsage()
        assert usage.prompt_tokens == 0
        assert usage.completion_tokens == 0
        assert usage.total_tokens == 0

        usage = TokenUsage(prompt_tokens=100, completion_tokens=50, total_tokens=150)
        assert usage.prompt_tokens == 100
        assert usage.completion_tokens == 50
        assert usage.total_tokens == 150

    def test_token_bonus_calculation(self):
        """Test token bonus calculation with sqrt formula"""
        service = AgentGrowthService()

        # Test edge cases
        assert service.calculate_token_bonus(0) == 0
        assert service.calculate_token_bonus(99) == 0  # Below threshold (99 < 100)

        # Test formula: floor(sqrt(tokens/100))
        assert service.calculate_token_bonus(100) == 1  # sqrt(1) = 1
        assert service.calculate_token_bonus(400) == 2  # sqrt(4) = 2
        assert service.calculate_token_bonus(900) == 3  # sqrt(9) = 3
        assert service.calculate_token_bonus(1000) == 3  # sqrt(10) = 3.16 -> 3
        assert service.calculate_token_bonus(10000) == 10  # sqrt(100) = 10
        assert service.calculate_token_bonus(100000) == 31  # sqrt(1000) = 31.6 -> 31

    def test_score_constants(self):
        """Test scoring constants"""
        service = AgentGrowthService()
        assert service.SCORE_PER_DISCUSSION == 10
        assert service.SCORE_PER_TASK == 10

    def test_score_calculation_components(self):
        """Test that score components are calculated correctly"""
        stats = AgentStats(agent_id=unique_agent_id())
        stats.discussion_count = 5
        stats.tasks_completed = 3
        stats.total_tokens_used = 1000

        service = AgentGrowthService()
        service._recalculate_scores(stats)

        # Verify component scores
        assert stats.discussion_score == 50  # 5 * 10
        assert stats.task_score == 30  # 3 * 10
        assert stats.token_bonus_score == 3  # sqrt(1000/100) = sqrt(10) = 3

        # Verify total score
        assert stats.score == 83  # 50 + 30 + 3

    def test_add_discussion_score(self):
        """Test adding discussion score"""
        service = AgentGrowthService()
        agent_id = unique_agent_id()

        result = service.add_discussion_score(agent_id, tokens_used=200)

        assert result["score_gained"] == 10
        assert result["discussion_count"] == 1

        # Add another discussion
        result = service.add_discussion_score(agent_id, tokens_used=300)

        assert result["score_gained"] == 10
        assert result["discussion_count"] == 2
        # Total tokens = 500, bonus = sqrt(5) = 2
        assert result["total_score"] == 22  # 20 + 2 bonus

    def test_add_task_score(self):
        """Test adding task score"""
        service = AgentGrowthService()
        agent_id = unique_agent_id()

        # First set up an agent with a completed task
        stats = service.get_agent_stats(agent_id)
        stats.tasks_completed = 1

        result = service.add_task_score(agent_id, tokens_used=500)

        assert result["score_gained"] == 10
        assert result["task_score"] == 10

    def test_score_persistence(self):
        """Test that scores are persisted correctly"""
        service = AgentGrowthService()
        agent_id = unique_agent_id()

        # Add discussion score
        service.add_discussion_score(agent_id, tokens_used=150)

        # Retrieve stats and verify
        stats = service.get_agent_stats(agent_id)
        assert stats.discussion_count == 1
        assert stats.discussion_score == 10
        assert stats.total_tokens_used == 150
        # Token bonus: sqrt(150/100) = sqrt(1.5) = 1
        assert stats.token_bonus_score == 1
        assert stats.score == 11  # 10 + 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
