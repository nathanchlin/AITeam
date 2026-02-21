class GameStateManager:
    def __init__(self):
        self.current_state = 'menu'  # menu, playing, paused, game_over
        self.high_score = 0
        self.games_played = 0
        
    def start_game(self):
        """开始新游戏"""
        self.current_state = 'playing'
        self.games_played += 1
        
    def pause_game(self):
        """暂停游戏"""
        if self.current_state == 'playing':
            self.current_state = 'paused'
            
    def resume_game(self):
        """恢复游戏"""
        if self.current_state == 'paused':
            self.current_state = 'playing'
            
    def end_game(self, final_score):
        """结束游戏"""
        self.current_state = 'game_over'
        if final_score > self.high_score:
            self.high_score = final_score
            
    def back_to_menu(self):
        """返回主菜单"""
        self.current_state = 'menu'