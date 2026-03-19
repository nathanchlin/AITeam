from typing import Dict, List, Optional
from datetime import datetime
import uuid
import json
import os
from app.agents.base import BaseAgent, create_agent
from app.models.schemas import AgentType, AgentStatus, Task, TaskStatus


class AgentManager:
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.tasks: Dict[str, Task] = {}
        self.data_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'agents.json')
        self._load_agents()

    def _load_agents(self):
        """Load persisted agents from file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for agent_data in data.get('agents', []):
                        # Validate required fields before loading
                        if not agent_data.get('id'):
                            print(f"[AgentManager] Warning: Agent missing id: {agent_data.get('name', 'Unknown')}")
                            continue  # Skip invalid agent
                        if not agent_data.get('name'):
                            print(f"[AgentManager] Warning: Agent missing name: {agent_data.get('id', 'Unknown')}")
                            agent_data['name'] = 'Unknown'  # Provide default

                        # Convert string type back to AgentType enum
                        agent_type_str = agent_data.get('type', 'assistant')
                        try:
                            agent_type = AgentType(agent_type_str)
                        except ValueError:
                            print(f"[AgentManager] Warning: Unknown agent type '{agent_type_str}' for agent {agent_data.get('id')}, using CUSTOM")
                            agent_type = AgentType.CUSTOM

                        agent = create_agent(
                            name=agent_data.get('name', 'Unknown'),
                            agent_type=agent_type,
                            description=agent_data.get('description'),
                            custom_prompt=agent_data.get('custom_prompt'),
                            position=agent_data.get('position'),
                            display_type=agent_data.get('display_type'),
                        )
                        # Restore original ID and timestamps
                        agent.id = agent_data.get('id', agent.id)
                        agent.created_at = datetime.fromisoformat(agent_data['created_at']) if agent_data.get('created_at') else agent.created_at
                        agent.updated_at = datetime.fromisoformat(agent_data['updated_at']) if agent_data.get('updated_at') else agent.updated_at
                        agent.status = AgentStatus.IDLE  # Always start as idle

                        self.agents[agent.id] = agent

                print(f"[AgentManager] Loaded {len(self.agents)} agents from storage")
            except Exception as e:
                print(f"[AgentManager] Error loading agents: {e}")

    def _save_agents(self):
        """Persist agents to file"""
        try:
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)

            data = {
                'agents': [
                    {
                        'id': agent.id,
                        'name': agent.name,
                        'type': agent.type.value if hasattr(agent.type, 'value') else str(agent.type),
                        'display_type': agent.display_type,
                        'description': agent.description,
                        'custom_prompt': agent.custom_prompt,
                        'position': agent.position,
                        'created_at': agent.created_at.isoformat() if agent.created_at else None,
                        'updated_at': agent.updated_at.isoformat() if agent.updated_at else None,
                    }
                    for agent in self.agents.values()
                ],
                'saved_at': datetime.utcnow().isoformat(),
            }

            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[AgentManager] Error saving agents: {e}")

    def create_agent(
        self,
        name: str,
        agent_type: AgentType,
        description: Optional[str] = None,
        custom_prompt: Optional[str] = None,
        position: Optional[Dict[str, float]] = None,
        display_type: Optional[str] = None,
    ) -> BaseAgent:
        agent = create_agent(name, agent_type, description, custom_prompt, position, display_type)
        self.agents[agent.id] = agent
        self._save_agents()  # Persist after creation
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
        display_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
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
        if display_type is not None:
            agent.display_type = display_type
        if tags is not None:
            agent.tags = tags

        agent.updated_at = datetime.utcnow()
        self._save_agents()  # Persist after update
        return agent

    def delete_agent(self, agent_id: str) -> bool:
        if agent_id in self.agents:
            del self.agents[agent_id]
            self._save_agents()  # Persist after deletion
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
