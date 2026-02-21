class GameStats:
    """游戏统计信息"""
    def __init__(self):
        self.score = 0
        self.lives = 3
        self.level = 1
        self.high_score = 0
        
    def add_score(self, points):
        """增加分数"""
        self.score += points
        if self.score > self.high_score:
            self.high_score = self.score
            
    def lose_life(self):
        """失去一条生命"""
        self.lives -= 1
        return self.lives <= 0
        
    def next_level(self):
        """进入下一关"""
        self.level += 1
        return self.level