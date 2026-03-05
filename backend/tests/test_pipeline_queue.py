"""Tests for Pipeline Queue functionality."""
import asyncio
import pytest
from app.services.pipeline_queue import PipelineQueueService, QueuedPipeline
from app.services.coordinator import CoordinatorService


from app.models.schemas import Plan, PlanStatus


from datetime import datetime
from unittest.mock import MagicMock, AsyncMock, patch
import uuid


@pytest.fixture
def queue_service():
    """Create a fresh queue service for each test."""
    service = PipelineQueueService()
    coordinator = CoordinatorService()
    service.set_coordinator(coordinator)
    yield service


    service.running.clear()
    service.queue.clear()


    yield service


class TestBasicEnqueue:
    """Test basic enqueue functionality."""

    def test_empty_queue_starts_immediately(queue_service):
        """When queue is empty, pipeline should start immediately."""
        plan_id = str(uuid.uuid4())

        result = asyncio.get_event_loop().run_until_complete(
            queue_service.enqueue(
                plan_id=plan_id,
                request="Test pipeline",
                target_output="web-app",
                selected_agent_ids=[]
            )
        )

        assert result["status"] == "started"
        assert result["queue_position"] == 0
        assert result["running_count"] == 1
        assert result["queue_length"] == 0
        assert plan_id in queue_service.running



    def test_full_queue_enqueues_pipelines(queue_service):
        """When at capacity, new pipelines should be queued."""
        # Fill the queue to capacity
        plan_ids = []
        for i in range(PipelineQueueService.MAX_concurrent):
            plan_id = str(uuid.uuid4())
            plan_ids.append(plan_id)
            result = asyncio.get_event_loop().run_until_complete(
                queue_service.enqueue(
                    plan_id=plan_id,
                    request=f"Pipeline {i+1}",
                    target_output="web-app",
                    selected_agent_ids=[]
                )
            )
            assert result["status"] == "started", f"Pipeline {i+1} should start"

        # Next pipeline should be queued
        queued_plan_id = str(uuid.uuid4())
        result = asyncio.get_event_loop().run_until_complete(
            queue_service.enqueue(
                plan_id=queued_plan_id,
                request="Queued pipeline",
                target_output="web-app",
                selected_agent_ids=[]
            )
        )

        assert result["status"] == "queued"
        assert result["queue_position"] == 1
        assert result["running_count"] == PipelineQueueService.max_concurrent
        assert result["queue_length"] == 1
        assert queued_plan_id not in queue_service.running
        assert queued_plan_id in [p.plan_id for p in queue_service.queue]

    def test_queue_position_updates_on_dequeue(queue_service):
        """Test that queue positions update correctly when pipelines complete."""
        # Start multiple pipelines
        plan_ids = []
        for i in range(PipelineQueueService.max_concurrent + 2):
            plan_id = str(uuid.uuid4())
            plan_ids.append(plan_id)
            asyncio.get_event_loop().run_until_complete(
                queue_service.enqueue(
                    plan_id=plan_id,
                    request=f"Pipeline {i+1}",
                    target_output="web-app",
                    selected_agent_ids=[]
                )
            )

        # Verify first 5 are running
        assert len(queue_service.running) == PipelineQueueService.max_concurrent

        # Verify queue positions
        for i, item in enumerate(queue_service.queue):
            assert item.position == i + 1

        # Complete first pipeline
        first_plan_id = plan_ids[0]
        asyncio.get_event_loop().run_until_complete(
            queue_service.on_pipeline_complete(first_plan_id)
        )

        # Verify queue moved up
        assert len(queue_service.queue) == 1
        assert queue_service.queue[0].position == 1
        assert plan_ids[5] in queue_service.running  # 6th should now be running

    def test_cancel_queued_pipeline(queue_service):
        """Test canceling a pipeline from the queue."""
        # Fill queue
        plan_ids = []
        for i in range(PipelineQueueService.max_concurrent + 2):
            plan_id = str(uuid.uuid4())
            plan_ids.append(plan_id)
            asyncio.get_event_loop().run_until_complete(
                queue_service.enqueue(
                    plan_id=plan_id,
                    request=f"Pipeline {i+1}",
                    target_output="web-app",
                    selected_agent_ids=[]
                )
            )

        # Cancel the second queued pipeline (index 1 in queue, position 2)
        cancelled_id = queue_service.queue[1].plan_id
        result = asyncio.get_event_loop().run_until_complete(
            queue_service.cancel_pipeline(cancelled_id)
        )

        assert result is True
        assert cancelled_id not in [p.plan_id for p in queue_service.queue]

        # Verify positions updated
        for i, item in enumerate(queue_service.queue):
            assert item.position == i + 1

    def test_cancel_running_pipeline_fails(queue_service):
        """Test that canceling a running pipeline fails."""
        # Start a pipeline
        plan_id = str(uuid.uuid4())
        asyncio.get_event_loop().run_until_complete(
            queue_service.enqueue(
                plan_id=plan_id,
                request="Test pipeline",
                target_output="web-app",
                selected_agent_ids=[]
            )
        )

        # Try to cancel running pipeline
        result = asyncio.get_event_loop().run_until_complete(
            queue_service.cancel_pipeline(plan_id)
        )

        assert result is False  # Cannot cancel running pipeline

    def test_get_queue_status(queue_service):
        """Test getting queue status."""
        # Start and queue some pipelines
        for i in range(PipelineQueueService.max_concurrent + 1):
            plan_id = str(uuid.uuid4())
            asyncio.get_event_loop().run_until_complete(
                queue_service.enqueue(
                    plan_id=plan_id,
                    request=f"Pipeline {i+1}",
                    target_output="web-app",
                    selected_agent_ids=[]
                )
            )

        status = queue_service.get_queue_status()

        assert status["running_count"] == PipelineQueueService.max_concurrent
        assert status["queue_length"] == 1
        assert status["max_concurrent"] == PipelineQueueService.max_concurrent
        assert len(status["running_pipelines"]) == PipelineQueueService.max_concurrent
        assert len(status["queued_pipelines"]) == 1

    def test_get_plan_queue_position(queue_service):
        """Test getting plan queue position."""
        # Start and queue pipelines
        plan_ids = []
        for i in range(PipelineQueueService.max_concurrent + 1):
            plan_id = str(uuid.uuid4())
            plan_ids.append(plan_id)
            asyncio.get_event_loop().run_until_complete(
                queue_service.enqueue(
                    plan_id=plan_id,
                    request=f"Pipeline {i+1}",
                    target_output="web-app",
                    selected_agent_ids=[]
                )
            )

        # Check running pipeline position
        running_pos = queue_service.get_plan_queue_position(plan_ids[0])
        assert running_pos["status"] == "running"
        assert running_pos["position"] == 0

        # Check queued pipeline position
        queued_pos = queue_service.get_plan_queue_position(plan_ids[-1])
        assert queued_pos["status"] == "queued"
        assert queued_pos["position"] == 1

        # Check non-existent pipeline
        none_pos = queue_service.get_plan_queue_position("non-existent")
        assert none_pos is None

    def test_clear_queue(queue_service):
        """Test clearing the queue."""
        # Queue multiple pipelines
        for i in range(PipelineQueueService.max_concurrent + 3):
            plan_id = str(uuid.uuid4())
            asyncio.get_event_loop().run_until_complete(
                queue_service.enqueue(
                    plan_id=plan_id,
                    request=f"Pipeline {i+1}",
                    target_output="web-app",
                    selected_agent_ids=[]
                )
            )

        initial_queue_length = len(queue_service.queue)
        assert initial_queue_length == 3

        # Clear queue
        count = asyncio.get_event_loop().run_until_complete(
            queue_service.clear_queue()
        )

        assert count == 3
        assert len(queue_service.queue) == 0
        # Running pipelines should not be affected
        assert len(queue_service.running) == PipelineQueueService.max_concurrent


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
