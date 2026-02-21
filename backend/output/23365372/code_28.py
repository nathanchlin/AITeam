# 配置代理组
config = {
    'global_settings': {
        'collection_interval': 30,
        'history_size': 100
    }
}

# 创建监控管理器
monitor_manager = AgentMonitorManager(config)

# 添加代理组
agent_group1 = ["agent1", "agent2", "agent3"]
monitor_manager.add_agent_group("web_servers", agent_group1)

# 获取最佳代理
best_agent = monitor_manager.get_best_agent("web_servers")
print(f"Best agent selected: {best_agent}")

# 获取当前指标
metrics = monitor_manager.get_metrics("web_servers")
print("Current metrics:", metrics)

# 获取特定代理的历史数据
history = monitor_manager.monitors["web_servers"].get_history_metrics("agent1", count=5)
print("History metrics for agent1:", history)

# 关闭监控器
monitor_manager.shutdown()