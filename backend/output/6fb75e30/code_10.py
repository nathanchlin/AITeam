class ScoreManager:
    def __init__(self):
        self.current_score = 0
        self.high_score = self._load_high_score()
        self.combo = 0
        self.max_combo = 0
    
    def add_score(self, points):
        """增加分数"""
        self.current_score += points * (1 + self.combo * 0.1)
        self.combo += 1
        self.max_combo = max(self.max_combo, self.combo)
        EventSystem.emit("score_updated", {"score": self.current_score, "combo": self.combo})
    
    def reset_combo(self):
        """重置连击"""
        self.combo = 0
    
    def save_high_score(self):
        """保存最高分"""
        if self.current_score > self.high_score:
            self.high_score = self.current_score
            self._save_high_score(self.high_score)
    
    def _load_high_score(self):
        """加载最高分"""
        # 实现从持久化存储加载最高分
        return 0
    
    def _save_high_score(self, score):
        """保存最高分"""
        # 实现保存最高分到持久化存储
        pass