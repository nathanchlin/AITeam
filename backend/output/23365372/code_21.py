class AgentManager:
    """代理管理器"""
    def __init__(self, storage_path: str = "agents.json"):
        self.agents: Dict[str, Agent] = {}
        self.storage_path = storage_path
        self.load_agents()
    
    def register_agent(self, agent: Agent) -> bool:
        """注册代理"""
        if agent.agent_id in self.agents:
            return False
        
        agent.status = AgentStatus.ONLINE
        agent.last_heartbeat = datetime.now()
        self.agents[agent.agent_id] = agent
        self.save_agents()
        return True
    
    def update_agent(self, agent_id: str, **kwargs) -> bool:
        """更新代理信息"""
        if agent_id not in self.agents:
            return False
        
        agent = self.agents[agent_id]
        
        # 更新基本信息
        if "host" in kwargs:
            agent.host = kwargs["host"]
        if "port" in kwargs:
            agent.port = kwargs["port"]
        if "capabilities" in kwargs:
            agent.capabilities = kwargs["capabilities"]
        if "max_concurrent_tasks" in kwargs:
            agent.max_concurrent_tasks = kwargs["max_concurrent_tasks"]
        if "metadata" in kwargs:
            agent.metadata.update(kwargs["metadata"])
        
        # 更新心跳时间
        agent.last_heartbeat = datetime.now()
        self.save_agents()
        return True
    
    def update_agent_status(self, agent_id: str, status: AgentStatus) -> bool:
        """更新代理状态"""
        if agent_id not in self.agents:
            return False
        
        self.agents[agent_id].status = status
        self.agents[agent_id].last_heartbeat = datetime.now()
        self.save_agents()
        return True
    
    def heartbeat(self, agent_id: str) -> bool:
        """代理心跳"""
        if agent_id not in self.agents:
            return False
        
        self.agents[agent_id].last_heartbeat = datetime.now()
        if self.agents[agent_id].status == AgentStatus.OFFLINE:
            self.agents[agent_id].status = AgentStatus.ONLINE
        self.save_agents()
        return True
    
    def offline_agent(self, agent_id: str, reason: str = None) -> bool:
        """下线代理"""
        if agent_id not in self.agents:
            return False
        
        self.agents[agent_id].status = AgentStatus.OFFLINE
        if reason:
            self.agents[agent_id].metadata["offline_reason"] = reason
        self.save_agents()
        return True
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """获取代理"""
        return self.agents.get(agent_id)
    
    def get_agents_by_status(self, status: AgentStatus) -> List[Agent]:
        """根据状态获取代理列表"""
        return [agent for agent in self.agents.values() if agent.status == status]
    
    def get_agents_by_capability(self, capability: str, status: AgentStatus = AgentStatus.ONLINE) -> List[Agent]:
        """根据能力和状态获取代理列表"""
        return [
            agent for agent in self.agents.values() 
            if capability in agent.capabilities and agent.status == status
        ]
    
    def select_agent(self, required_capabilities: List[str], 
                    max_concurrent_tasks: int = 1) -> Optional[Agent]:
        """选择满足条件的代理"""
        # 筛选满足所有能力且状态为在线的代理
        candidates = [
            agent for agent in self.agents.values()
            if agent.status == AgentStatus.ONLINE
            and all(cap in agent.capabilities for cap in required_capabilities)
            and agent.current_tasks < agent.max_concurrent_tasks
            and agent.max_concurrent_tasks >= max_concurrent_tasks
        ]
        
        if not candidates:
            return None
        
        # 选择当前任务数最少的代理
        return min(candidates, key=lambda x: x.current_tasks)
    
    def increment_task(self, agent_id: str) -> bool:
        """增加代理任务计数"""
        if agent_id not in self.agents:
            return False
        
        agent = self.agents[agent_id]
        if agent.current_tasks < agent.max_concurrent_tasks:
            agent.current_tasks += 1
            if agent.current_tasks >= agent.max_concurrent_tasks:
                agent.status = AgentStatus.BUSY
            self.save_agents()
            return True
        return False
    
    def decrement_task(self, agent_id: str) -> bool:
        """减少代理任务计数"""
        if agent_id not in self.agents:
            return False
        
        agent = self.agents[agent_id]
        if agent.current_tasks > 0:
            agent.current_tasks -= 1
            if agent.current_tasks < agent.max_concurrent_tasks and agent.status == AgentStatus.BUSY:
                agent.status = AgentStatus.ONLINE
            self.save_agents()
            return True
        return False
    
    def cleanup_inactive_agents(self, timeout_seconds: int = 300) -> List[str]:
        """清理不活跃的代理"""
        now = datetime.now()
        inactive_agents = []
        
        for agent_id, agent in list(self.agents.items()):
            if (now - agent.last_heartbeat).total_seconds() > timeout_seconds:
                inactive_agents.append(agent_id)
                del self.agents[agent_id]
        
        if inactive_agents:
            self.save_agents()
        
        return inactive_agents
    
    def save_agents(self) -> None:
        """保存代理数据到文件"""
        data = {
            agent_id: agent.to_dict() 
            for agent_id, agent in self.agents.items()
        }
        
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_agents(self) -> None:
        """从文件加载代理数据"""
        if not os.path.exists(self.storage_path):
            return
        
        with open(self.storage_path, 'r') as f:
            data = json.load(f)
        
        self.agents = {
            agent_id: Agent.from_dict(agent_data)
            for agent_id, agent_data in data.items()
        }
    
    def get_all_agents(self) -> Dict[str, Agent]:
        """获取所有代理"""
        return self.agents.copy()
    
    def remove_agent(self, agent_id: str) -> bool:
        """移除代理"""
        if agent_id in self.agents:
            del self.agents[agent_id]
            self.save_agents()
            return True
        return False