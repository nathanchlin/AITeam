class ScoreSystem:
    def __init__(self):
        self.score = 0
        self.combo_multiplier = 1
        self.max_combo = 0
        self.current_combo = 0
        
    def add_score(self, points, brick_type=None):
        """添加分数，支持连击系统"""
        if brick_type:
            # 根据砖块类型计算基础分数
            base_points = self._get_brick_points(brick_type)
            points = base_points * self.combo_multiplier
            
        self.score += points
        self.current_combo += 1
        self.max_combo = max(self.max_combo, self.current_combo)
        
        # 更新连击倍数
        if self.current_combo >= 5:
            self.combo_multiplier = 3
        elif self.current_combo >= 3:
            self.combo_multiplier = 2
        else:
            self.combo_multiplier = 1
            
    def reset_combo(self):
        """重置连击计数器"""
        self.current_combo = 0
        self.combo_multiplier = 1
        
    def _get_brick_points(self, brick_type):
        """根据砖块类型返回基础分数"""
        points_map = {
            'normal': 10,
            'strong': 20,
            'super_strong': 30,
            'special': 50
        }
        return points_map.get(brick_type, 10)


class LifeSystem:
    def __init__(self, initial_lives=3):
        self.lives = initial_lives
        self.max_lives = initial_lives
        self.game_over = False
        
    def lose_life(self):
        """减少一条生命"""
        self.lives -= 1
        if self.lives <= 0:
            self.lives = 0
            self.game_over = True
            
    def gain_life(self):
        """增加一条生命（例如通过特殊道具）"""
        if self.lives < self.max_lives:
            self.lives += 1
            
    def reset(self):
        """重置生命值系统"""
        self.lives = self.max_lives
        self.game_over = False