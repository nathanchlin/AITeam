class ScoreSystem:
    def __init__(self):
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.distance_traveled = 0
        self.obstacles_avoided = 0
        
    def update(self, ninja, obstacles):
        # 更新距离得分
        self.distance_traveled += ninja.speed * 0.1
        self.score += int(self.distance_traveled * 0.01)
        
        # 检查是否避开障碍物
        for obstacle in obstacles:
            if obstacle.passed and not obstacle.scored:
                self.obstacles_avoided += 1
                obstacle.scored = True
                self.score += 10 * (1 + self.combo * 0.1)
                self.combo += 1
                self.max_combo = max(self.max_combo, self.combo)
                
        # 重置连击如果碰撞
        if ninja.is_hit:
            self.combo = 0
            
    def get_final_score(self):
        # 计算最终得分（包含连击加成等）
        return int(self.score * (1 + self.max_combo * 0.05))