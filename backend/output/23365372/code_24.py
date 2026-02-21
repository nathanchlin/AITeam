import time
from functools import lru_cache

class OptimizedAgentSelector(AgentSelector):
    def __init__(self, *args, cache_ttl=10, **kwargs):
        super().__init__(*args, **kwargs)
        self.cache_ttl = cache_ttl  # 缓存有效期(秒)
        self.score_cache = {}  # 缓存 {agent_id: (score, timestamp)}
    
    @lru_cache(maxsize=1000)
    def calculate_score(self, agent_id: str) -> float:
        """带缓存的得分计算"""
        agent = self.agents.get(agent_id)
        if not agent:
            return -float('inf')
        
        # 检查缓存是否有效
        if agent_id in self.score_cache:
            score, timestamp = self.score_cache[agent_id]
            if time.time() - timestamp < self.cache_ttl:
                return score
        
        # 计算新得分
        score = super().calculate_score(agent)
        
        # 更新缓存
        self.score_cache[agent_id] = (score, time.time())
        
        return score