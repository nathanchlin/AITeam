class ScoreSystem:
    def __init__(self):
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.last_hit_time = 0
        self.combo_timeout = 3000  # 3秒内击中敌人保持连击
        
    def add_score(self, points, enemy_type="basic"):
        """根据敌人和连击情况添加分数"""
        import time
        current_time = time.time() * 1000  # 转换为毫秒
        
        # 检查连击
        if current_time - self.last_hit_time <= self.combo_timeout:
            self.combo += 1
        else:
            self.combo = 1
            
        self.last_hit_time = current_time
        
        # 根据敌人类型和连击计算得分
        enemy_multiplier = {
            "basic": 1,
            "fast": 1.5,
            "tank": 2.0,
            "boss": 5.0
        }
        
        combo_multiplier = 1 + (self.combo - 1) * 0.1  # 每次连击增加10%分数
        
        total_points = int(points * enemy_multiplier.get(enemy_type, 1) * combo_multiplier)
        self.score += total_points
        
        # 更新最高连击
        if self.combo > self.max_combo:
            self.max_combo = self.combo
            
        return total_points
    
    def reset_combo(self):
        """重置连击"""
        self.combo = 0
    
    def get_score(self):
        """获取当前分数"""
        return self.score
    
    def get_combo(self):
        """获取当前连击数"""
        return self.combo