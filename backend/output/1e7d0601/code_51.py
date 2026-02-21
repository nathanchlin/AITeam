class DifficultyManager:
    def __init__(self):
        self.base_enemy_speed = 2.0
        self.base_enemy_health = 100
        self.base_enemy_damage = 10
        self.spawn_rate = 2.0  # 敌机生成间隔(秒)
        
    def get_adjusted_stats(self, level_difficulty):
        adjusted_stats = {
            'enemy_speed': self.base_enemy_speed * (1 + 0.2 * level_difficulty),
            'enemy_health': int(self.base_enemy_health * (1 + 0.3 * level_difficulty)),
            'enemy_damage': int(self.base_enemy_damage * (1 + 0.15 * level_difficulty)),
            'spawn_rate': max(0.5, self.spawn_rate - 0.1 * level_difficulty)
        }
        return adjusted_stats