from enum import Enum
from datetime import datetime
from typing import Dict, List, Optional
import json
import os

class AgentStatus(Enum):
    """代理状态枚举"""
    ONLINE = "online"      # 在线
    OFFLINE = "offline"    # 离线
    BUSY = "busy"         # 忙碌
    MAINTENANCE = "maintenance"  # 维护中

class Agent:
    """代理类"""
    def __init__(self, agent_id: str, host: str, port: int, 
                 capabilities: List[str], max_concurrent_tasks: int = 1):
        self.agent_id = agent_id
        self.host = host
        self.port = port
        self.capabilities = capabilities
        self.max_concurrent_tasks = max_concurrent_tasks
        self.current_tasks = 0
        self.status = AgentStatus.OFFLINE
        self.last_heartbeat = datetime.now()
        self.register_time = datetime.now()
        self.metadata = {}
    
    def to_dict(self) -> Dict:
        """将代理对象转换为字典"""
        return {
            "agent_id": self.agent_id,
            "host": self.host,
            "port": self.port,
            "capabilities": self.capabilities,
            "max_concurrent_tasks": self.max_concurrent_tasks,
            "current_tasks": self.current_tasks,
            "status": self.status.value,
            "last_heartbeat": self.last_heartbeat.isoformat(),
            "register_time": self.register_time.isoformat(),
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Agent':
        """从字典创建代理对象"""
        agent = cls(
            agent_id=data["agent_id"],
            host=data["host"],
            port=data["port"],
            capabilities=data["capabilities"],
            max_concurrent_tasks=data.get("max_concurrent_tasks", 1)
        )
        agent.current_tasks = data.get("current_tasks", 0)
        agent.status = AgentStatus(data.get("status", "offline"))
        agent.last_heartbeat = datetime.fromisoformat(data.get("last_heartbeat", datetime.now().isoformat()))
        agent.register_time = datetime.fromisoformat(data.get("register_time", datetime.now().isoformat()))
        agent.metadata = data.get("metadata", {})
        return agent