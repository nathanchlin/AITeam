"""
Redis Pub/Sub broadcast manager for cross-process WebSocket communication.

This module enables Celery workers to broadcast messages to WebSocket clients
through Redis Pub/Sub, with FastAPI subscribing and forwarding to connected clients.
"""

import asyncio
import json
import threading
from typing import Dict, Any, Optional, Set, Callable
import redis
from app.config import settings


class BroadcastManager:
    """
    Manages cross-process communication via Redis Pub/Sub.

    Usage:
    1. Celery workers call broadcast() to send messages
    2. FastAPI subscribes and forwards to WebSocket clients
    """

    CHANNEL_NAME = "aiteam:broadcast"

    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or settings.redis_url
        self._redis_client: Optional[redis.Redis] = None
        self._pubsub: Optional[redis.client.PubSub] = None
        self._subscribers: Set[Callable] = set()
        self._listener_thread: Optional[threading.Thread] = None
        self._running = False

    @property
    def redis_client(self) -> redis.Redis:
        """Get or create Redis client."""
        if self._redis_client is None:
            self._redis_client = redis.from_url(self.redis_url)
        return self._redis_client

    def publish(self, message: Dict[str, Any]) -> None:
        """
        Publish a message to the broadcast channel (sync version for Celery).

        Args:
            message: The message dict to broadcast
        """
        try:
            data = json.dumps(message, ensure_ascii=False)
            self.redis_client.publish(self.CHANNEL_NAME, data)
        except Exception as e:
            print(f"[BroadcastManager] Publish error: {e}")

    async def broadcast(self, message: Dict[str, Any]) -> None:
        """
        Broadcast a message to all subscribers (async version).

        Args:
            message: The message dict to broadcast
        """
        # Run publish in thread pool for async compatibility
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.publish, message)

    def subscribe(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """
        Subscribe to broadcast messages.

        Args:
            callback: Function to call when a message is received
        """
        self._subscribers.add(callback)

        # Start listener if not already running
        if not self._running:
            self._start_listener()

    def unsubscribe(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """
        Unsubscribe from broadcast messages.

        Args:
            callback: The callback to remove
        """
        self._subscribers.discard(callback)

        # Stop listener if no more subscribers
        if not self._subscribers and self._running:
            self._stop_listener()

    def _start_listener(self) -> None:
        """Start the Redis Pub/Sub listener thread."""
        if self._running:
            return

        self._running = True
        self._pubsub = self.redis_client.pubsub()
        self._pubsub.subscribe(self.CHANNEL_NAME)

        self._listener_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._listener_thread.start()

        print(f"[BroadcastManager] Started listener on channel {self.CHANNEL_NAME}")

    def _stop_listener(self) -> None:
        """Stop the Redis Pub/Sub listener."""
        self._running = False

        if self._pubsub:
            self._pubsub.unsubscribe()
            self._pubsub.close()
            self._pubsub = None

        if self._listener_thread:
            self._listener_thread.join(timeout=5)
            self._listener_thread = None

        print(f"[BroadcastManager] Stopped listener")

    def _listen_loop(self) -> None:
        """Main listener loop running in background thread."""
        while self._running:
            try:
                message = self._pubsub.get_message(timeout=1)
                if message and message["type"] == "message":
                    data = json.loads(message["data"])
                    # Notify all subscribers
                    for callback in list(self._subscribers):
                        try:
                            callback(data)
                        except Exception as e:
                            print(f"[BroadcastManager] Callback error: {e}")
            except redis.ConnectionError:
                print(f"[BroadcastManager] Redis connection lost, retrying...")
                import time
                time.sleep(5)
            except Exception as e:
                if self._running:
                    print(f"[BroadcastManager] Listen error: {e}")

    def close(self) -> None:
        """Clean up resources."""
        self._stop_listener()
        if self._redis_client:
            self._redis_client.close()
            self._redis_client = None


class WebSocketBridge:
    """
    Bridge between Redis Pub/Sub and WebSocket manager.

    This class subscribes to Redis broadcasts and forwards them
    to connected WebSocket clients.
    """

    def __init__(self, broadcast_manager: BroadcastManager):
        self.broadcast_manager = broadcast_manager
        self.websocket_manager = None

    def connect(self, websocket_manager) -> None:
        """
        Connect the bridge to a WebSocket manager.

        Args:
            websocket_manager: The WebSocket manager instance
        """
        self.websocket_manager = websocket_manager
        self.broadcast_manager.subscribe(self._on_broadcast)
        print("[WebSocketBridge] Connected to WebSocket manager")

    def disconnect(self) -> None:
        """Disconnect from WebSocket manager."""
        self.broadcast_manager.unsubscribe(self._on_broadcast)
        self.websocket_manager = None
        print("[WebSocketBridge] Disconnected from WebSocket manager")

    def _on_broadcast(self, message: Dict[str, Any]) -> None:
        """
        Handle a broadcast message from Redis.

        Args:
            message: The message to forward to WebSocket clients
        """
        if self.websocket_manager:
            # Schedule async broadcast in the event loop
            asyncio.create_task(self._async_broadcast(message))

    async def _async_broadcast(self, message: Dict[str, Any]) -> None:
        """Async wrapper for WebSocket broadcast."""
        if self.websocket_manager:
            await self.websocket_manager.broadcast(message)


# Global instances
broadcast_manager = BroadcastManager()
websocket_bridge = WebSocketBridge(broadcast_manager)
