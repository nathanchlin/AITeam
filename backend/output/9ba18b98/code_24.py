from enum import Enum, auto

class GameState(Enum):
    """游戏状态枚举"""
    MENU = auto()        # 菜单界面
    STARTING = auto()    # 游戏开始前
    PLAYING = auto()     # 游戏进行中
    PAUSED = auto()      # 游戏暂停
    GAME_OVER = auto()   # 游戏结束
    EXITING = auto()     # 游戏退出

class GameStateManager:
    """游戏状态管理器"""
    def __init__(self):
        self.current_state = GameState.MENU
        self.previous_state = None
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        
    def change_state(self, new_state):
        """改变游戏状态"""
        if new_state != self.current_state:
            self.previous_state = self.current_state
            self.current_state = new_state
            
    def get_state(self):
        """获取当前状态"""
        return self.current_state
        
    def is_playing(self):
        """检查是否在游戏进行中"""
        return self.current_state == GameState.PLAYING
        
    def is_paused(self):
        """检查是否暂停状态"""
        return self.current_state == GameState.PAUSED
        
    def is_game_over(self):
        """检查是否游戏结束"""
        return self.current_state == GameState.GAME_OVER
        
    def reset_game(self):
        """重置游戏数据"""
        self.score = 0
        self.level = 1
        self.lines_cleared = 0