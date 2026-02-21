class GameStateManager:
    def __init__(self, game_system):
        self.game_system = game_system
        
    def start_game(self):
        """开始游戏"""
        self.game_system.game_state = "PLAYING"
        self._reset_game()
        
    def pause_game(self):
        """暂停游戏"""
        if self.game_system.game_state == "PLAYING":
            self.game_system.game_state = "PAUSED"
            
    def resume_game(self):
        """恢复游戏"""
        if self.game_system.game_state == "PAUSED":
            self.game_system.game_state = "PLAYING"
            
    def game_over(self):
        """游戏结束"""
        self.game_system.game_state = "GAME_OVER"
        
    def restart_game(self):
        """重新开始游戏"""
        self.game_system.game_state = "START"
        self._reset_game()
        self.start_game()
        
    def _reset_game(self):
        """重置游戏状态"""
        self.game_system.score = 0
        self.game_system.lives = self.game_system.max_lives
        self.game_system.combo = 0
        self.game_system.max_combo = 0
        self.game_system.combo_timer = 0
        self.game_system.combo_multiplier = 1.0
        self.game_system.last_extra_life_score = 0