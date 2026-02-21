import time
import heapq
import statistics
from dataclasses import dataclass
from typing import List, Dict, Optional
import random

@dataclass
class AgentMetrics:
    """代理性能指标数据类"""
    agent_id: str
    cpu_usage: float  # CPU使用率 (0-100)
    memory_usage: float  # 内存使用率 (0-100)
    network_io: float  # 网络I/O使用率 (0-100)
    response_times: List[float]  # 响应时间历史记录
    last_updated: float  # 最后更新时间戳
    
    @property
    def avg_response_time(self) -> float:
        """计算平均响应时间"""
        if not self.response_times:
            return float('inf')
        return statistics.mean(self.response_times)
    
    @property
    def current_load(self) -> float:
        """计算当前综合负载 (0-100)"""
        return (self.cpu_usage + self.memory_usage + self.network_io) / 3

@dataclass
class AgentInfo:
    """代理完整信息"""
    agent_id: str
    host: str
    port: int
    weight: float = 1.0  # 权重系数
    is_healthy: bool = True  # 健康状态
    metrics: Optional[AgentMetrics] = None

class AgentSelector:
    def __init__(self, agents: List[AgentInfo], weights: Dict[str, float] = None):
        """
        初始化代理选择器
        
        :param agents: 代理列表
        :param weights: 各因素的权重字典，格式为 {'load': x, 'performance': y, 'latency': z}
                       默认为 {'load': 0.4, 'performance': 0.3, 'latency': 0.3}
        """
        self.agents = {agent.agent_id: agent for agent in agents}
        self.weights = weights or {'load': 0.4, 'performance': 0.3, 'latency': 0.3}
        
        # 验证权重总和为1
        total_weight = sum(self.weights.values())
        if not abs(total_weight - 1.0) < 1e-6:
            raise ValueError(f"Weights must sum to 1.0, got {total_weight}")
    
    def update_agent_metrics(self, agent_id: str, metrics: AgentMetrics):
        """更新代理的指标数据"""
        if agent_id in self.agents:
            self.agents[agent_id].metrics = metrics
    
    def calculate_score(self, agent: AgentInfo) -> float:
        """
        计算代理的综合得分
        
        得分越高，代理越适合被选择。算法考虑以下因素：
        1. 负载得分 - 负载越低得分越高
        2. 性能得分 - 响应时间越短得分越高
        3. 延迟得分 - 网络延迟越低得分越高
        
        最终得分 = 负载得分 * 负载权重 + 性能得分 * 性能权重 + 延迟得分 * 延迟权重
        """
        if not agent.is_healthy or not agent.metrics:
            return -float('inf')  # 不健康或无指标的代理不参与选择
        
        metrics = agent.metrics
        
        # 1. 负载得分 (0-1范围，负载越低得分越高)
        load_score = 1.0 - (metrics.current_load / 100.0)
        
        # 2. 性能得分 (0-1范围，响应时间越短得分越高)
        # 使用对数函数映射响应时间，避免极小响应时间导致得分过高
        min_rt = 0.01  # 最小响应时间，避免除以0
        normalized_rt = min(metrics.avg_response_time, 10.0)  # 最大归一化响应时间为10秒
        performance_score = 1.0 - (math.log(normalized_rt / min_rt + 1) / math.log(10.0 / min_rt + 1))
        
        # 3. 延迟得分 (0-1范围，延迟越低得分越高)
        # 这里假设metrics中包含latency属性，如果没有需要修改
        if hasattr(metrics, 'latency'):
            normalized_latency = min(metrics.latency, 1000.0)  # 最大归一化延迟为1000ms
            latency_score = 1.0 - (normalized_latency / 1000.0)
        else:
            latency_score = 0.5  # 如果没有延迟信息，给中等分数
        
        # 计算加权总分
        total_score = (
            load_score * self.weights['load'] +
            performance_score * self.weights['performance'] +
            latency_score * self.weights['latency']
        )
        
        # 应用权重系数
        return total_score * agent.weight
    
    def select_agent(self, exclude_agents: List[str] = None) -> Optional[AgentInfo]:
        """
        选择最佳代理
        
        :param exclude_agents: 要排除的代理ID列表
        :return: 选中的代理，如果没有可用代理则返回None
        """
        exclude_agents = exclude_agents or []
        
        # 过滤掉排除的代理和不健康的代理
        candidates = [
            agent for agent in self.agents.values() 
            if agent.agent_id not in exclude_agents and agent.is_healthy
        ]
        
        if not candidates:
            return None
        
        # 计算每个候选代理的得分
        scored_agents = [(self.calculate_score(agent), agent) for agent in candidates]
        
        # 使用堆选择得分最高的代理
        _, best_agent = max(scored_agents, key=lambda x: x[0])
        
        return best_agent
    
    def select_agents_round_robin(self, count: int, exclude_agents: List[str] = None) -> List[AgentInfo]:
        """
        使用轮询方式选择多个代理，确保负载均衡
        
        :param count: 需要选择的代理数量
        :param exclude_agents: 要排除的代理ID列表
        :return: 选中的代理列表
        """
        exclude_agents = exclude_agents or []
        
        # 过滤掉排除的代理和不健康的代理
        candidates = [
            agent for agent in self.agents.values() 
            if agent.agent_id not in exclude_agents and agent.is_healthy
        ]
        
        if not candidates:
            return []
        
        # 按得分排序
        scored_agents = sorted(candidates, key=lambda a: self.calculate_score(a), reverse=True)
        
        # 选择前count个代理，如果不足则返回所有
        return scored_agents[:count]
    
    def select_agents_weighted_random(self, count: int, exclude_agents: List[str] = None) -> List[AgentInfo]:
        """
        使用加权随机方式选择多个代理
        
        :param count: 需要选择的代理数量
        :param exclude_agents: 要排除的代理ID列表
        :return: 选中的代理列表
        """
        exclude_agents = exclude_agents or []
        
        # 过滤掉排除的代理和不健康的代理
        candidates = [
            agent for agent in self.agents.values() 
            if agent.agent_id not in exclude_agents and agent.is_healthy
        ]
        
        if not candidates:
            return []
        
        # 计算每个代理的权重
        scored_agents = [(self.calculate_score(agent), agent) for agent in candidates]
        total_score = sum(score for score, _ in scored_agents)
        
        if total_score <= 0:
            # 如果所有代理得分都很低，则随机选择
            return random.sample(candidates, min(count, len(candidates)))
        
        # 根据权重进行随机选择
        selected = []
        remaining = count
        
        while remaining > 0 and len(candidates) > 0:
            # 计算每个代理的选择概率
            weights = [score / total_score for score, _ in scored_agents]
            
            # 根据权重随机选择一个代理
            chosen_idx = random.choices(range(len(candidates)), weights=weights, k=1)[0]
            chosen_agent = scored_agents[chosen_idx][1]
            
            selected.append(chosen_agent)
            remaining -= 1
            
            # 从候选列表中移除已选择的代理
            candidates.pop(chosen_idx)
            scored_agents.pop(chosen_idx)
            
            # 重新计算总分
            total_score = sum(score for score, _ in scored_agents)
        
        return selected