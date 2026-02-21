class DifficultyManager:
    def __init__(self):
        self.base_enemy_count = 3
        self.base_enemy_speed = 2.0
        self.base_spawn_rate = 2000  # 毫秒
        
        self.current_enemy_count = self.base_enemy_count
        self.current_enemy_speed = self.base_enemy_speed
        self.current_spawn_rate = self.base_spawn_rate
        
        self.difficulty_thresholds = [
            {"score": 100, "multiplier": 1.2},
            {"score": 300, "multiplier": 1.5},
            {"score": 600, "multiplier": 1.8},
            {"score": 1000, "multiplier": 2.2},
            {"score": 1500, "multiplier": 2.5}
        ]
    
    def update_difficulty(self, score):
        """根据分数更新游戏难度"""
        for threshold in self.difficulty_thresholds:
            if score >= threshold["score"]:
                multiplier = threshold["multiplier"]
            else:
                break
        
        # 应用难度倍数
        self.current_enemy_count = min(
            int(self.base_enemy_count * multiplier), 
            15  # 最大敌人数量限制
        )
        self.current_enemy_speed = min(
            self.base_enemy_speed * multiplier, 
            8.0  # 最大敌人速度限制
        )
        self.current_spawn_rate = max(
            int(self.base_spawn_rate / multiplier), 
            500  # 最小生成间隔(毫秒)
        )
        
        return {
            "enemy_count": self.current_enemy_count,
            "enemy_speed": self.current_enemy_speed,
            "spawn_rate": self.current_spawn_rate
        }