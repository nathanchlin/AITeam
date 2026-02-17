import asyncio
from typing import Optional, Dict, Any
from datetime import datetime
from app.services.agent_manager import agent_manager
from app.models.schemas import TaskStatus, AgentStatus


class TaskExecutor:
    def __init__(self):
        self.running_tasks: Dict[str, asyncio.Task] = {}

    async def execute_task(
        self,
        task_id: str,
        websocket_manager: Optional[Any] = None,
    ):
        task = agent_manager.get_task(task_id)
        if not task or not task.agent_id:
            return

        agent = agent_manager.get_agent(task.agent_id)
        if not agent:
            return

        # Update task status
        agent_manager.update_task(task_id, status=TaskStatus.RUNNING, progress=0.0)
        agent.update_status(AgentStatus.WORKING)

        # Notify via WebSocket
        if websocket_manager:
            await websocket_manager.broadcast({
                "type": "task_update",
                "data": {
                    "task_id": task_id,
                    "status": "running",
                    "progress": 0.0,
                }
            })
            await websocket_manager.broadcast({
                "type": "agent_update",
                "data": {
                    "agent_id": agent.id,
                    "status": "working",
                }
            })

        full_response = ""
        step = 0

        try:
            task_input = f"{task.title}\n\n{task.description or ''}".strip()

            async for update in agent.execute_task(task_input):
                step += 1

                if update["type"] == "thinking":
                    agent_manager.add_thinking_step(task_id, step, update["content"])
                    if websocket_manager:
                        await websocket_manager.broadcast({
                            "type": "thinking",
                            "data": {
                                "task_id": task_id,
                                "agent_id": agent.id,
                                "agent_name": agent.name,
                                "step": step,
                                "thought": update["content"],
                            }
                        })

                elif update["type"] == "stream":
                    full_response += update["content"]
                    progress = min(0.9, 0.1 + step * 0.05)
                    agent_manager.update_task(task_id, progress=progress)

                    if websocket_manager:
                        await websocket_manager.broadcast({
                            "type": "stream",
                            "data": {
                                "task_id": task_id,
                                "agent_id": agent.id,
                                "content": update["content"],
                                "progress": progress,
                            }
                        })

                elif update["type"] == "complete":
                    agent_manager.update_task(
                        task_id,
                        status=TaskStatus.COMPLETED,
                        progress=1.0,
                        result=full_response
                    )
                    agent.update_status(AgentStatus.IDLE)
                    agent.current_task_id = None

                    if websocket_manager:
                        await websocket_manager.broadcast({
                            "type": "task_update",
                            "data": {
                                "task_id": task_id,
                                "status": "completed",
                                "progress": 1.0,
                                "result": full_response,
                            }
                        })
                        await websocket_manager.broadcast({
                            "type": "agent_update",
                            "data": {
                                "agent_id": agent.id,
                                "status": "idle",
                            }
                        })

        except Exception as e:
            agent_manager.update_task(
                task_id,
                status=TaskStatus.FAILED,
                result=f"任务执行失败：{str(e)}"
            )
            agent.update_status(AgentStatus.ERROR)

            if websocket_manager:
                await websocket_manager.broadcast({
                    "type": "task_update",
                    "data": {
                        "task_id": task_id,
                        "status": "failed",
                        "error": str(e),
                    }
                })
                await websocket_manager.broadcast({
                    "type": "agent_update",
                    "data": {
                        "agent_id": agent.id,
                        "status": "error",
                    }
                })

    def start_task(self, task_id: str, websocket_manager: Optional[Any] = None):
        if task_id in self.running_tasks:
            return False

        task = asyncio.create_task(self.execute_task(task_id, websocket_manager))
        self.running_tasks[task_id] = task
        return True

    def cancel_task(self, task_id: str):
        if task_id in self.running_tasks:
            self.running_tasks[task_id].cancel()
            del self.running_tasks[task_id]
            return True
        return False


# Global instance
task_executor = TaskExecutor()
