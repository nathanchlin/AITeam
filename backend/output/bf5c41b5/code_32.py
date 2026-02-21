class GameStateManager:
    def __init__(self):
        self.current_state = GameState.MENU
        self.previous_state = None
        self.state_stack = []
        self.state_transitions = {
            GameState.MENU: {
                "start": GameState.PLAYING,
                "settings": GameState.SETTINGS,
                "quit": None
            },
            GameState.PLAYING: {
                "pause": GameState.PAUSED,
                "game_over": GameState.GAME_OVER,
                "level_complete": GameState.LEVEL_COMPLETE
            },
            GameState.PAUSED: {
                "resume": GameState.PLAYING,
                "menu": GameState.MENU,
                "restart": GameState.PLAYING
            },
            GameState.GAME_OVER: {
                "restart": GameState.PLAYING,
                "menu": GameState.MENU
            },
            GameState.LEVEL_COMPLETE: {
                "next_level": GameState.PLAYING,
                "menu": GameState.MENU
            },
            GameState.SETTINGS: {
                "back": GameState.MENU
            }
        }
    
    def change_state(self, new_state, transition_type=None):
        """改变游戏状态"""
        if transition_type and self.current_state in self.state_transitions:
            valid_transitions = self.state_transitions[self.current_state]
            if transition_type in valid_transitions:
                if valid_transitions[transition_type] == new_state:
                    self.previous_state = self.current_state
                    self.current_state = new_state
                    return True
        
        # 如果没有指定转换类型或无效转换，直接尝试设置状态
        if new_state in [GameState.MENU, GameState.PLAYING, GameState.PAUSED, 
                        GameState.GAME_OVER, GameState.LEVEL_COMPLETE, GameState.SETTINGS]:
            self.previous_state = self.current_state
            self.current_state = new_state
            return True
        
        return False
    
    def push_state(self, new_state):
        """压入新状态到栈中"""
        self.state_stack.append(self.current_state)
        self.current_state = new_state
    
    def pop_state(self):
        """弹出状态栈顶状态，恢复到前一个状态"""
        if self.state_stack:
            self.current_state = self.state_stack.pop()
            return True
        return False
    
    def reset_to_menu(self):
        """重置到主菜单状态"""
        self.current_state = GameState.MENU
        self.state_stack = []
        self.previous_state = None
    
    def get_state(self):
        """获取当前状态"""
        return self.current_state
    
    def is_state(self, state):
        """检查当前是否为指定状态"""
        return self.current_state == state
    
    def get_valid_transitions(self):
        """获取当前状态下的有效转换"""
        return self.state_transitions.get(self.current_state, {})