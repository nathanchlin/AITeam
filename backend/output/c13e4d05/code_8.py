class ScoreSystem:
    # 增加分数
    def add_score(self):
        self.current_score += self.score_increment
        if self.current_score > self.high_score:
            self.high_score = self.current_score
    
    # 获取当前分数
    def get_current_score(self):
        return self.current_score
    
    # 获取最高分
    def get_high_score(self):
        return self.high_score
    
    # 重置分数
    def reset_score(self):
        self.current_score = 0
    
    # 保存最高分
    def save_high_score(self):
        pass
    
    # 加载最高分
    def load_high_score(self):
        pass