class GameState:
    """游戏状态管理类"""
    
    # 游戏状态常量
    MENU = "menu"          # 菜单状态
    STARTING = "starting"  # 开始状态
    PLAYING = "playing"    # 进行中状态
    PAUSED = "paused"      # 暂停状态
    GAME_OVER = "game_over"  # 游戏结束状态
    WIN = "win"            # 胜利状态
    
    def __init__(self):
        """初始化游戏状态"""
        self.current_state = self.MENU
        self.score = 0
        self.lives = 3
        self.level = 1
        self.high_score = 0
        
    def reset_game(self):
        """重置游戏状态"""
        self.score = 0
        self.lives = 3
        self.level = 1
        self.current_state = self.STARTING
        
    def add_score(self, points):
        """增加分数"""
        self.score += points
        if self.score > self.high_score:
            self.high_score = self.score
            
    def lose_life(self):
        """减少生命值"""
        self.lives -= 1
        if self.lives <= 0:
            self.current_state = self.GAME_OVER
            
    def check_win_condition(self, bricks):
        """检查胜利条件"""
        if not bricks:  # 如果所有砖块都被消除
            self.level += 1
            if self.level > 3:  # 假设只有3关
                self.current_state = self.WIN
            else:
                self.current_state = self.STARTING  # 进入下一关
                
    def toggle_pause(self):
        """切换暂停状态"""
        if self.current_state == self.PLAYING:
            self.current_state = self.PAUSED
        elif self.current_state == self.PAUSED:
            self.current_state = self.PLAYING
            
    def start_game(self):
        """开始游戏"""
        self.current_state = self.PLAYING
        
    def back_to_menu(self):
        """返回菜单"""
        self.current_state = self.MENU