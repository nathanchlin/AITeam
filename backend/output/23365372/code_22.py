# 创建代理管理器
manager = AgentManager("agents.json")

# 创建新代理
agent1 = Agent(
    agent_id="agent-001",
    host="192.168.1.100",
    port=8080,
    capabilities=["data_processing", "ml_training"],
    max_concurrent_tasks=3
)

# 注册代理
manager.register_agent(agent1)
print(f"Agent {agent1.agent_id} registered successfully")

# 更新代理状态
manager.update_agent_status("agent-001", AgentStatus.BUSY)
print(f"Agent {agent1.agent_id} status updated to busy")

# 心跳
manager.heartbeat("agent-001")
print("Heartbeat received")

# 选择代理
selected = manager.select_agent(["data_processing"])
if selected:
    print(f"Selected agent: {selected.agent_id}")
    manager.increment_task(selected.agent_id)
else:
    print("No available agent found")

# 下线代理
manager.offline_agent("agent-001", "Scheduled maintenance")
print(f"Agent {agent1.agent_id} offline")

# 清理不活跃代理
inactive = manager.cleanup_inactive_agents()
if inactive:
    print(f"Cleaned up inactive agents: {inactive}")