"""Pipeline Queue Service for managing concurrent pipeline execution.

This module implements a queue mechanism for pipelines:
- Maximum 1 concurrent pipeline can run at a time
- Additional pipelines are queued and started when a slot becomes available
- Thread-safe using asyncio.Lock
"""

import asyncio
from collections import deque
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import traceback


@dataclass
class QueuedPipeline:
    """Represents a pipeline in the queue."""
    plan_id: str
    request: str
    target_output: str
    selected_agent_ids: List[str]
    skip_discussion: bool = False
    quick_mode: bool = False  # 🚀 快速模式
    queued_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    position: int = 0


class PipelineQueueService:
    """Service for managing pipeline execution queue.

    Ensures maximum concurrent pipelines limit is respected and
    automatically starts queued pipelines when slots become available.
    """

    MAX_CONCURRENT = 1

    def __init__(self):
        self.queue: deque[QueuedPipeline] = deque()
        self.running: Dict[str, QueuedPipeline] = {}
        self._lock = asyncio.Lock()
        self._coordinator = None
        self._websocket_manager = None

    def set_coordinator(self, coordinator):
        """Set the coordinator service reference."""
        self._coordinator = coordinator

    def set_websocket_manager(self, ws_manager):
        """Set the websocket manager for broadcasting."""
        self._websocket_manager = ws_manager

    async def enqueue(
        self,
        plan_id: str,
        request: str,
        target_output: str,
        selected_agent_ids: List[str],
        skip_discussion: bool = False,
        quick_mode: bool = False
    ) -> dict:
        """Add a pipeline to the queue.

        If there's room to run immediately, starts execution.
        Otherwise, adds to the waiting queue.

        Returns:
            dict with queue status including position and whether started
        """
        async with self._lock:
            # Update positions for items already in queue
            for i, item in enumerate(self.queue):
                item.position = i + 1

            pipeline = QueuedPipeline(
                plan_id=plan_id,
                request=request,
                target_output=target_output,
                selected_agent_ids=selected_agent_ids,
                skip_discussion=skip_discussion,
                quick_mode=quick_mode,
                position=len(self.queue) + 1,
            )

            # Check if we can start immediately
            if len(self.running) < self.MAX_CONCURRENT:
                pipeline.position = 0  # 0 means running
                pipeline.started_at = datetime.now()
                self.running[plan_id] = pipeline
                # Start execution outside the lock
                asyncio.create_task(self._start_pipeline(pipeline))
                return {
                    "status": "started",
                    "plan_id": plan_id,
                    "queue_position": 0,
                    "running_count": len(self.running),
                    "queue_length": len(self.queue),
                }
            else:
                # Add to queue
                self.queue.append(pipeline)
                return {
                    "status": "queued",
                    "plan_id": plan_id,
                    "queue_position": pipeline.position,
                    "running_count": len(self.running),
                    "queue_length": len(self.queue),
                    "estimated_wait": f"{pipeline.position} pipeline(s) ahead",
                }

    async def _start_pipeline(self, pipeline: QueuedPipeline):
        """Start pipeline execution."""
        if not self._coordinator:
            print("[PipelineQueue] Error: Coordinator not set")
            return

        try:
            print(f"[PipelineQueue] Starting pipeline {pipeline.plan_id}")

            # Broadcast queue update
            await self._broadcast_queue_update()

            # Run the full pipeline
            await self._coordinator.analyze_request(pipeline.plan_id)
            if not pipeline.skip_discussion:
                await self._coordinator.organize_discussion(pipeline.plan_id)
            await self._coordinator.generate_plan(pipeline.plan_id)
            await self._coordinator.execute_plan(pipeline.plan_id)

        except Exception as e:
            print(f"[PipelineQueue] Error executing pipeline {pipeline.plan_id}: {e}")
            traceback.print_exc()
        finally:
            # Pipeline completed (success or error), notify queue
            await self.on_pipeline_complete(pipeline.plan_id)

    async def on_pipeline_complete(self, plan_id: str):
        """Handle pipeline completion. Start next in queue if available."""
        async with self._lock:
            # Remove from running
            if plan_id in self.running:
                del self.running[plan_id]
                print(f"[PipelineQueue] Pipeline {plan_id} completed. Running: {len(self.running)}, Queued: {len(self.queue)}")

            # Start next if available and under limit
            if self.queue and len(self.running) < self.MAX_CONCURRENT:
                next_pipeline = self.queue.popleft()
                next_pipeline.position = 0
                next_pipeline.started_at = datetime.now()
                self.running[next_pipeline.plan_id] = next_pipeline

                print(f"[PipelineQueue] Starting next pipeline {next_pipeline.plan_id} from queue")

                # Update positions for the remaining queued items after dequeue
                for i, item in enumerate(self.queue):
                    item.position = i + 1

                # Start execution outside the lock
                asyncio.create_task(self._start_pipeline(next_pipeline))
            else:
                # Update positions for remaining items in queue when nothing new starts
                for i, item in enumerate(self.queue):
                    item.position = i + 1

        # Broadcast queue update
        await self._broadcast_queue_update()

    async def _broadcast_queue_update(self):
        """Broadcast queue status update to WebSocket clients."""
        if self._websocket_manager:
            try:
                await self._websocket_manager.broadcast({
                    "type": "queue_update",
                    "data": self.get_queue_status()
                })
            except Exception as e:
                print(f"[PipelineQueue] Error broadcasting queue update: {e}")

    def get_queue_status(self) -> dict:
        """Get current queue status."""
        return {
            "running_count": len(self.running),
            "max_concurrent": self.MAX_CONCURRENT,
            "queue_length": len(self.queue),
            "running_pipelines": [
                {
                    "plan_id": p.plan_id,
                    "request": p.request[:100] + "..." if len(p.request) > 100 else p.request,
                    "target_output": p.target_output,
                    "started_at": p.started_at.isoformat() if p.started_at else None,
                }
                for p in self.running.values()
            ],
            "queued_pipelines": [
                {
                    "plan_id": p.plan_id,
                    "request": p.request[:100] + "..." if len(p.request) > 100 else p.request,
                    "target_output": p.target_output,
                    "position": p.position,
                    "queued_at": p.queued_at.isoformat(),
                }
                for p in self.queue
            ],
        }

    def get_plan_queue_position(self, plan_id: str) -> Optional[dict]:
        """Get queue position for a specific plan."""
        # Check if running
        if plan_id in self.running:
            return {
                "status": "running",
                "position": 0,
                "started_at": self.running[plan_id].started_at.isoformat() if self.running[plan_id].started_at else None,
            }

        # Check if in queue
        for i, p in enumerate(self.queue):
            if p.plan_id == plan_id:
                return {
                    "status": "queued",
                    "position": i + 1,
                    "queued_at": p.queued_at.isoformat(),
                }

        # Not found
        return None

    async def cancel_pipeline(self, plan_id: str) -> bool:
        """Cancel a pipeline from the queue.

        Returns:
            True if cancelled, False if not found or already running
        """
        async with self._lock:
            # Can't cancel if already running
            if plan_id in self.running:
                return False

            # Find and remove from queue
            for i, p in enumerate(self.queue):
                if p.plan_id == plan_id:
                    self.queue.remove(p)
                    # Update positions
                    for j, item in enumerate(self.queue):
                        item.position = j + 1
                    print(f"[PipelineQueue] Cancelled pipeline {plan_id} from queue")
                    await self._broadcast_queue_update()
                    return True

            return False

    async def clear_queue(self) -> int:
        """Clear all pipelines from the queue (not running ones).

        Returns:
            Number of pipelines removed
        """
        async with self._lock:
            count = len(self.queue)
            self.queue.clear()
            print(f"[PipelineQueue] Cleared {count} pipelines from queue")
            await self._broadcast_queue_update()
            return count


# Global singleton instance
pipeline_queue = PipelineQueueService()
