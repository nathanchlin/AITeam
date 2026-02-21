class GameState:
    def __init__(self):
        self.state = "MENU"  # MENU, PLAYING, GAME_OVER
        self.score = 0
        self.high_score = 0
    
    def transition(self, new_state):
        """
        转换游戏状态
        :param new_state: 新状态 (MENU, PLAYING, GAME_OVER)
        """
        if new_state == "GAME_OVER" and self.score > self.high_score:
            self.high_score = self.score
        
        self.state = new_state
        self.score = 0 if new_state == "PLAYING" else self.score