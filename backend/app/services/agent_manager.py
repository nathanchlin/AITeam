from typing import Dict, List, Optional
from datetime import datetime
import uuid
from app.agents.base import BaseAgent, create_agent
from app.models.schemas import AgentType, AgentStatus, Task, TaskStatus


class AgentManager:
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.tasks: Dict[str, Task] = {}

    def create_agent(
        self,
        name: str,
        agent_type: AgentType,
        description: Optional[str] = None,
        custom_prompt: Optional[str] = None,
        position: Optional[Dict[str, float]] = None,
    ) -> BaseAgent:
        agent = create_agent(name, agent_type, description, custom_prompt, position)
        self.agents[agent.id] = agent
        return agent

    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        return self.agents.get(agent_id)

    def get_all_agents(self) -> List[BaseAgent]:
        return list(self.agents.values())

    def update_agent(
        self,
        agent_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        custom_prompt: Optional[str] = None,
        position: Optional[Dict[str, float]] = None,
        status: Optional[AgentStatus] = None,
    ) -> Optional[BaseAgent]:
        agent = self.agents.get(agent_id)
        if not agent:
            return None

        if name:
            agent.name = name
        if description is not None:
            agent.description = description
        if custom_prompt is not None:
            agent.custom_prompt = custom_prompt
        if position:
            agent.position = position
        if status:
            agent.status = status

        agent.updated_at = datetime.utcnow()
        return agent

    def delete_agent(self, agent_id: str) -> bool:
        if agent_id in self.agents:
            del self.agents[agent_id]
            return True
        return False

    def create_task(
        self,
        title: str,
        description: Optional[str] = None,
        agent_id: Optional[str] = None,
    ) -> Task:
        task_id = str(uuid.uuid4())
        task = Task(
            id=task_id,
            title=title,
            description=description,
            agent_id=agent_id,
            status=TaskStatus.PENDING,
        )
        self.tasks[task_id] = task
        return task

    def get_task(self, task_id: str) -> Optional[Task]:
        return self.tasks.get(task_id)

    def get_all_tasks(self) -> List[Task]:
        return list(self.tasks.values())

    def get_agent_tasks(self, agent_id: str) -> List[Task]:
        return [t for t in self.tasks.values() if t.agent_id == agent_id]

    def update_task(
        self,
        task_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        status: Optional[TaskStatus] = None,
        progress: Optional[float] = None,
        result: Optional[str] = None,
    ) -> Optional[Task]:
        task = self.tasks.get(task_id)
        if not task:
            return None

        if title:
            task.title = title
        if description is not None:
            task.description = description
        if status:
            task.status = status
            if status == TaskStatus.RUNNING:
                task.started_at = datetime.utcnow()
            elif status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                task.completed_at = datetime.utcnow()
        if progress is not None:
            task.progress = progress
        if result is not None:
            task.result = result

        task.updated_at = datetime.utcnow()
        return task

    def delete_task(self, task_id: str) -> bool:
        if task_id in self.tasks:
            del self.tasks[task_id]
            return True
        return False

    def assign_task(self, task_id: str, agent_id: str) -> Optional[Task]:
        task = self.tasks.get(task_id)
        agent = self.agents.get(agent_id)

        if not task or not agent:
            return None

        task.agent_id = agent_id
        task.updated_at = datetime.utcnow()
        agent.current_task_id = task_id
        agent.updated_at = datetime.utcnow()

        return task

    def add_thinking_step(self, task_id: str, step: int, thought: str, action: Optional[str] = None):
        task = self.tasks.get(task_id)
        if task:
            task.thinking_process.append({
                "step": step,
                "thought": thought,
                "action": action,
                "timestamp": datetime.utcnow().isoformat(),
            })


# Global instance
agent_manager = AgentManager()
