class HealthSystem:
    def __init__(self, game_system):
        self.game_system = game_system
        
    def take_damage(self, damage=1):
        """处理玩家受到伤害"""
        if self.game_system.game_state != "PLAYING":
            return
            
        self.game_system.lives -= damage
        
        # 受伤时重置连击
        self.game_system.combo = 0
        self.game_system.combo_multiplier = 1.0
        
        # 检查游戏是否结束
        if self.game_system.lives <= 0:
            self.game_system.game_state = "GAME_OVER"
            
    def add_life(self, count=1):
        """添加生命值"""
        if self.game_system.game_state != "PLAYING":
            return
            
        self.game_system.lives = min(
            self.game_system.lives + count,
            self.game_system.max_lives
        )
        
    def is_alive(self):
        """检查玩家是否存活"""
        return self.game_system.lives > 0