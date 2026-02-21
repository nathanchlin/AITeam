class GameController:
    def __init__(self):
        self.score_system = ScoreSystem()
        self.difficulty_manager = DifficultyManager()
        self.current_difficulty = self.difficulty_manager.update_difficulty(0)
        
    def on_enemy_destroyed(self, enemy_type="basic"):
        """敌人被摧毁时的处理"""
        points = 10  # 基础分数
        score_gained = self.score_system.add_score(points, enemy_type)
        
        # 更新难度
        self.current_difficulty = self.difficulty_manager.update_difficulty(
            self.score_system.get_score()
        )
        
        return score_gained
    
    def get_spawn_config(self):
        """获取当前敌人生成配置"""
        return {
            "count": self.current_difficulty["enemy_count"],
            "speed": self.current_difficulty["enemy_speed"],
            "spawn_rate": self.current_difficulty["spawn_rate"]
        }