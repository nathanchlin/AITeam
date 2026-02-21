import time
import threading
import psutil
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from collections import deque

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AgentMonitor")

@dataclass
class AgentMetrics:
    """代理性能指标数据类"""
    agent_id: str
    timestamp: float
    cpu_usage: float
    memory_usage: float
    network_io: Dict[str, float]
    disk_io: Dict[str, float]
    active_connections: int
    response_time: float
    error_rate: float
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return asdict(self)

class AgentMonitor:
    """代理监控器类"""
    
    def __init__(self, agent_ids: List[str], collection_interval: int = 30, 
                 history_size: int = 100):
        """
        初始化代理监控器
        
        :param agent_ids: 要监控的代理ID列表
        :param collection_interval: 数据收集间隔(秒)
        :param history_size: 保留的历史数据大小
        """
        self.agent_ids = agent_ids
        self.collection_interval = collection_interval
        self.history_size = history_size
        self.metrics_history: Dict[str, deque] = {
            agent_id: deque(maxlen=history_size) 
            for agent_id in agent_ids
        }
        self.current_metrics: Dict[str, AgentMetrics] = {}
        self._stop_event = threading.Event()
        self._monitor_thread = None
        self._lock = threading.Lock()
        
    def collect_agent_metrics(self, agent_id: str) -> Optional[AgentMetrics]:
        """
        收集单个代理的性能指标
        
        :param agent_id: 代理ID
        :return: 代理性能指标对象
        """
        try:
            # 在实际实现中，这里会通过API或SSH连接获取远程代理的数据
            # 这里使用本地系统数据作为示例
            
            # CPU使用率
            cpu_usage = psutil.cpu_percent(interval=1)
            
            # 内存使用情况
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            
            # 网络I/O
            network = psutil.net_io_counters()
            network_io = {
                'bytes_sent': network.bytes_sent,
                'bytes_recv': network.bytes_recv,
                'packets_sent': network.packets_sent,
                'packets_recv': network.packets_recv
            }
            
            # 磁盘I/O
            disk = psutil.disk_io_counters()
            disk_io = {
                'read_bytes': disk.read_bytes,
                'write_bytes': disk.write_bytes,
                'read_count': disk.read_count,
                'write_count': disk.write_count
            } if disk else {}
            
            # 活动连接数 (简化示例)
            active_connections = len(psutil.net_connections())
            
            # 响应时间 (模拟)
            response_time = 0.1 + (cpu_usage / 100) * 0.9
            
            # 错误率 (模拟)
            error_rate = 0.01 + (memory_usage / 100) * 0.05
            
            metrics = AgentMetrics(
                agent_id=agent_id,
                timestamp=time.time(),
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                network_io=network_io,
                disk_io=disk_io,
                active_connections=active_connections,
                response_time=response_time,
                error_rate=error_rate
            )
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting metrics for agent {agent_id}: {str(e)}")
            return None
    
    def update_metrics(self, agent_id: str, metrics: AgentMetrics):
        """
        更新代理指标数据
        
        :param agent_id: 代理ID
        :param metrics: 新的性能指标
        """
        with self._lock:
            self.current_metrics[agent_id] = metrics
            self.metrics_history[agent_id].append(metrics)
    
    def calculate_load_score(self, agent_id: str) -> float:
        """
        计算代理的负载评分 (0-1, 越低越好)
        
        :param agent_id: 代理ID
        :return: 负载评分
        """
        if agent_id not in self.current_metrics:
            return 1.0  # 默认高负载
            
        metrics = self.current_metrics[agent_id]
        
        # 计算加权负载分数
        cpu_weight = 0.3
        memory_weight = 0.2
        response_weight = 0.3
        error_weight = 0.2
        
        # 归一化各项指标 (0-1范围)
        cpu_score = metrics.cpu_usage / 100
        memory_score = metrics.memory_usage / 100
        response_score = min(metrics.response_time / 2, 1)  # 假设2秒为最大
        error_score = min(metrics.error_rate, 1)
        
        # 计算加权总分
        load_score = (
            cpu_weight * cpu_score +
            memory_weight * memory_score +
            response_weight * response_score +
            error_weight * error_score
        )
        
        return load_score
    
    def get_best_agent(self) -> Optional[str]:
        """
        根据当前负载情况选择最佳代理
        
        :return: 最佳代理ID
        """
        if not self.current_metrics:
            return None
            
        best_agent = None
        best_score = float('inf')
        
        for agent_id in self.agent_ids:
            score = self.calculate_load_score(agent_id)
            if score < best_score:
                best_score = score
                best_agent = agent_id
                
        return best_agent
    
    def monitor_loop(self):
        """监控主循环"""
        while not self._stop_event.is_set():
            for agent_id in self.agent_ids:
                metrics = self.collect_agent_metrics(agent_id)
                if metrics:
                    self.update_metrics(agent_id, metrics)
                    
            # 检查是否有代理负载过高
            for agent_id in self.agent_ids:
                if agent_id in self.current_metrics:
                    score = self.calculate_load_score(agent_id)
                    if score > 0.8:  # 负载阈值
                        logger.warning(f"Agent {agent_id} has high load score: {score:.2f}")
            
            time.sleep(self.collection_interval)
    
    def start(self):
        """启动监控"""
        if self._monitor_thread is None or not self._monitor_thread.is_alive():
            self._stop_event.clear()
            self._monitor_thread = threading.Thread(target=self.monitor_loop)
            self._monitor_thread.daemon = True
            self._monitor_thread.start()
            logger.info("Agent monitor started")
    
    def stop(self):
        """停止监控"""
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._stop_event.set()
            self._monitor_thread.join()
            logger.info("Agent monitor stopped")
    
    def get_current_metrics(self, agent_id: Optional[str] = None) -> Dict:
        """
        获取当前指标数据
        
        :param agent_id: 可选，指定代理ID。如果为None，返回所有代理
        :return: 指标数据字典
        """
        with self._lock:
            if agent_id:
                return {agent_id: self.current_metrics.get(agent_id)}
            return self.current_metrics.copy()
    
    def get_history_metrics(self, agent_id: str, count: Optional[int] = None) -> List[Dict]:
        """
        获取历史指标数据
        
        :param agent_id: 代理ID
        :param count: 要获取的记录数，None表示全部
        :return: 历史指标数据列表
        """
        if agent_id not in self.metrics_history:
            return []
            
        history = list(self.metrics_history[agent_id])
        if count is not None:
            history = history[-count:]
            
        return [metric.to_dict() for metric in history]

class AgentMonitorManager:
    """代理监控管理器"""
    
    def __init__(self, config: Dict):
        """
        初始化监控管理器
        
        :param config: 配置字典
        """
        self.config = config
        self.monitors: Dict[str, AgentMonitor] = {}
        self._load_config()
    
    def _load_config(self):
        """加载配置"""
        self.agent_groups = self.config.get('agent_groups', {})
        self.global_settings = self.config.get('global_settings', {
            'collection_interval': 30,
            'history_size': 100
        })
    
    def add_agent_group(self, group_name: str, agent_ids: List[str]):
        """添加代理组"""
        if group_name not in self.monitors:
            monitor = AgentMonitor(
                agent_ids=agent_ids,
                collection_interval=self.global_settings['collection_interval'],
                history_size=self.global_settings['history_size']
            )
            self.monitors[group_name] = monitor
            self.agent_groups[group_name] = agent_ids
            monitor.start()
    
    def remove_agent_group(self, group_name: str):
        """移除代理组"""
        if group_name in self.monitors:
            self.monitors[group_name].stop()
            del self.monitors[group_name]
            if group_name in self.agent_groups:
                del self.agent_groups[group_name]
    
    def get_best_agent(self, group_name: str) -> Optional[str]:
        """
        从指定组获取最佳代理
        
        :param group_name: 代理组名称
        :return: 最佳代理ID
        """
        if group_name in self.monitors:
            return self.monitors[group_name].get_best_agent()
        return None
    
    def get_metrics(self, group_name: Optional[str] = None, 
                   agent_id: Optional[str] = None) -> Dict:
        """
        获取指标数据
        
        :param group_name: 代理组名称
        :param agent_id: 代理ID
        :return: 指标数据
        """
        result = {}
        
        if group_name and group_name in self.monitors:
            if agent_id:
                metrics = self.monitors[group_name].get_current_metrics(agent_id)
                result[group_name] = metrics
            else:
                metrics = self.monitors[group_name].get_current_metrics()
                result[group_name] = metrics
        else:
            for group, monitor in self.monitors.items():
                metrics = monitor.get_current_metrics()
                result[group] = metrics
                
        return result
    
    def shutdown(self):
        """关闭所有监控器"""
        for monitor in self.monitors.values():
            monitor.stop()
        self.monitors.clear()