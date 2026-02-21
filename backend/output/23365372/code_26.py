# 创建代理列表
agents = [
    AgentInfo("agent1", "192.168.1.1", 8080, weight=1.2),
    AgentInfo("agent2", "192.168.1.2", 8080, weight=0.8),
    AgentInfo("agent3", "192.168.1.3", 8080, weight=1.0),
]

# 创建选择器
selector = AdaptiveAgentSelector(
    agents, 
    weights={'load': 0.5, 'performance': 0.3, 'latency': 0.2}
)

# 模拟更新代理指标
def update_metrics():
    for agent_id in selector.agents:
        metrics = AgentMetrics(
            agent_id=agent_id,
            cpu_usage=random.uniform(20, 80),
            memory_usage=random.uniform(30, 70),
            network_io=random.uniform(10, 60),
            response_times=[random.uniform(0.1, 0.5) for _ in range(10)],
            last_updated=time.time()
        )
        selector.update_agent_metrics(agent_id, metrics)

# 选择代理
update_metrics()
best_agent = selector.select_agent()
print(f"Selected agent: {best_agent.agent_id}")

# 记录选择结果
selector.record_selection_result(best_agent.agent_id, random.uniform(0.1, 0.5), True)

# 使用轮询方式选择多个代理
selected_agents = selector.select_agents_round_robin(2)
print(f"Selected agents for round-robin: {[a.agent_id for a in selected_agents]}")

# 使用加权随机方式选择多个代理
selected_agents = selector.select_agents_weighted_random(2)
print(f"Selected agents for weighted random: {[a.agent_id for a in selected_agents]}")