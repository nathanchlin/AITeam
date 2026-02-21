class AdaptiveAgentSelector(OptimizedAgentSelector):
    def __init__(self, *args, adaptation_window=60, **kwargs):
        super().__init__(*args, **kwargs)
        self.adaptation_window = adaptation_window  # 自适应调整窗口(秒)
        self.selection_history = []  # 选择历史记录
        self.performance_metrics = {}  # 性能指标记录
    
    def record_selection_result(self, agent_id: str, response_time: float, success: bool):
        """记录选择结果，用于后续权重调整"""
        timestamp = time.time()
        self.selection_history.append((timestamp, agent_id, response_time, success))
        
        # 清理过期的历史记录
        cutoff_time = timestamp - self.adaptation_window
        self.selection_history = [
            record for record in self.selection_history 
            if record[0] > cutoff_time
        ]
        
        # 更新性能指标
        if agent_id not in self.performance_metrics:
            self.performance_metrics[agent_id] = []
        
        if success:
            self.performance_metrics[agent_id].append(response_time)
        
        # 定期调整权重
        if len(self.selection_history) % 10 == 0:
            self._adjust_weights()
    
    def _adjust_weights(self):
        """根据历史性能数据调整权重"""
        if not self.selection_history:
            return
        
        # 计算每个代理的平均性能
        agent_performance = {}
        for agent_id in self.agents:
            if agent_id in self.performance_metrics and self.performance_metrics[agent_id]:
                avg_performance = statistics.mean(self.performance_metrics[agent_id])
                agent_performance[agent_id] = avg_performance
            else:
                agent_performance[agent_id] = float('inf')
        
        # 计算整体性能基准
        valid_performances = [p for p in agent_performance.values() if p != float('inf')]
        if not valid_performances:
            return
        
        baseline_performance = statistics.mean(valid_performances)
        
        # 根据性能差异调整权重
        performance_weight = self.weights['performance']
        load_weight = self.weights['load']
        latency_weight = self.weights['latency']
        
        # 如果整体性能低于预期，增加性能权重
        if baseline_performance > 1.0:  # 假设1秒是可接受的基准
            performance_weight *= 1.1
            load_weight *= 0.95
            latency_weight *= 0.95
        
        # 归一化权重
        total = performance_weight + load_weight + latency_weight
        self.weights['performance'] = performance_weight / total
        self.weights['load'] = load_weight / total
        self.weights['latency'] = latency_weight / total