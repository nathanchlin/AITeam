"""Tests for Pipeline Queue functionality."""
import asyncio
import uuid
from unittest.mock import MagicMock

import pytest

from app.services.pipeline_queue import PipelineQueueService


@pytest.fixture
def queue_service(monkeypatch):
    """Create a fresh queue service for each test with background tasks disabled."""
    service = PipelineQueueService()

    def discard_task(coro):
        coro.close()
        return MagicMock()

    monkeypatch.setattr("app.services.pipeline_queue.asyncio.create_task", discard_task)

    yield service

    service.running.clear()
    service.queue.clear()


class TestBasicEnqueue:
    """Test basic enqueue functionality."""

    def test_empty_queue_starts_immediately(self, queue_service):
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

    def test_full_queue_enqueues_pipelines(self, queue_service):
        """When at capacity, new pipelines should be queued."""
        for i in range(PipelineQueueService.MAX_CONCURRENT):
            plan_id = str(uuid.uuid4())
            result = asyncio.get_event_loop().run_until_complete(
                queue_service.enqueue(
                    plan_id=plan_id,
                    request=f"Pipeline {i + 1}",
                    target_output="web-app",
                    selected_agent_ids=[]
                )
            )
            assert result["status"] == "started", f"Pipeline {i + 1} should start"

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
        assert result["running_count"] == PipelineQueueService.MAX_CONCURRENT
        assert result["queue_length"] == 1
        assert queued_plan_id not in queue_service.running
        assert queued_plan_id in [p.plan_id for p in queue_service.queue]

    def test_queue_position_updates_on_dequeue(self, queue_service):
        """Queued items should move up and the next pipeline should start on completion."""
        plan_ids = []
        for i in range(PipelineQueueService.MAX_CONCURRENT + 2):
            plan_id = str(uuid.uuid4())
            plan_ids.append(plan_id)
            asyncio.get_event_loop().run_until_complete(
                queue_service.enqueue(
                    plan_id=plan_id,
                    request=f"Pipeline {i + 1}",
                    target_output="web-app",
                    selected_agent_ids=[]
                )
            )

        assert len(queue_service.running) == PipelineQueueService.MAX_CONCURRENT

        for i, item in enumerate(queue_service.queue):
            assert item.position == i + 1

        first_plan_id = plan_ids[0]
        asyncio.get_event_loop().run_until_complete(
            queue_service.on_pipeline_complete(first_plan_id)
        )

        assert len(queue_service.queue) == 1
        assert queue_service.queue[0].position == 1
        assert plan_ids[PipelineQueueService.MAX_CONCURRENT] in queue_service.running

    def test_cancel_queued_pipeline(self, queue_service):
        """Test canceling a pipeline from the queue."""
        for i in range(PipelineQueueService.MAX_CONCURRENT + 2):
            plan_id = str(uuid.uuid4())
            asyncio.get_event_loop().run_until_complete(
                queue_service.enqueue(
                    plan_id=plan_id,
                    request=f"Pipeline {i + 1}",
                    target_output="web-app",
                    selected_agent_ids=[]
                )
            )

        cancelled_id = queue_service.queue[1].plan_id
        result = asyncio.get_event_loop().run_until_complete(
            queue_service.cancel_pipeline(cancelled_id)
        )

        assert result is True
        assert cancelled_id not in [p.plan_id for p in queue_service.queue]

        for i, item in enumerate(queue_service.queue):
            assert item.position == i + 1

    def test_cancel_running_pipeline_fails(self, queue_service):
        """Test that canceling a running pipeline fails."""
        plan_id = str(uuid.uuid4())
        asyncio.get_event_loop().run_until_complete(
            queue_service.enqueue(
                plan_id=plan_id,
                request="Test pipeline",
                target_output="web-app",
                selected_agent_ids=[]
            )
        )

        result = asyncio.get_event_loop().run_until_complete(
            queue_service.cancel_pipeline(plan_id)
        )

        assert result is False

    def test_get_queue_status(self, queue_service):
        """Test getting queue status."""
        for i in range(PipelineQueueService.MAX_CONCURRENT + 1):
            plan_id = str(uuid.uuid4())
            asyncio.get_event_loop().run_until_complete(
                queue_service.enqueue(
                    plan_id=plan_id,
                    request=f"Pipeline {i + 1}",
                    target_output="web-app",
                    selected_agent_ids=[]
                )
            )

        status = queue_service.get_queue_status()

        assert status["running_count"] == PipelineQueueService.MAX_CONCURRENT
        assert status["queue_length"] == 1
        assert status["max_concurrent"] == PipelineQueueService.MAX_CONCURRENT
        assert len(status["running_pipelines"]) == PipelineQueueService.MAX_CONCURRENT
        assert len(status["queued_pipelines"]) == 1

    def test_get_plan_queue_position(self, queue_service):
        """Test getting plan queue position."""
        plan_ids = []
        for i in range(PipelineQueueService.MAX_CONCURRENT + 1):
            plan_id = str(uuid.uuid4())
            plan_ids.append(plan_id)
            asyncio.get_event_loop().run_until_complete(
                queue_service.enqueue(
                    plan_id=plan_id,
                    request=f"Pipeline {i + 1}",
                    target_output="web-app",
                    selected_agent_ids=[]
                )
            )

        running_pos = queue_service.get_plan_queue_position(plan_ids[0])
        assert running_pos["status"] == "running"
        assert running_pos["position"] == 0

        queued_pos = queue_service.get_plan_queue_position(plan_ids[-1])
        assert queued_pos["status"] == "queued"
        assert queued_pos["position"] == 1

        none_pos = queue_service.get_plan_queue_position("non-existent")
        assert none_pos is None

    def test_clear_queue(self, queue_service):
        """Test clearing the queue."""
        for i in range(PipelineQueueService.MAX_CONCURRENT + 3):
            plan_id = str(uuid.uuid4())
            asyncio.get_event_loop().run_until_complete(
                queue_service.enqueue(
                    plan_id=plan_id,
                    request=f"Pipeline {i + 1}",
                    target_output="web-app",
                    selected_agent_ids=[]
                )
            )

        initial_queue_length = len(queue_service.queue)
        assert initial_queue_length == 3

        count = asyncio.get_event_loop().run_until_complete(
            queue_service.clear_queue()
        )

        assert count == 3
        assert len(queue_service.queue) == 0
        assert len(queue_service.running) == PipelineQueueService.MAX_CONCURRENT


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
