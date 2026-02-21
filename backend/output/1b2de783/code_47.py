class GameStateManager:
    def __init__(self):
        self.current_state = GameState.MENU
        self.previous_state = None
        self.state_stack = []
        self.state_transitions = {
            GameState.MENU: {
                "start": GameState.STARTING,
                "quit": "quit"
            },
            GameState.STARTING: {
                "complete": GameState.PLAYING
            },
            GameState.PLAYING: {
                "pause": GameState.PAUSED,
                "game_over": GameState.GAME_OVER
            },
            GameState.PAUSED: {
                "resume": GameState.PLAYING,
                "menu": GameState.MENU,
                "restart": GameState.RESTARTING
            },
            GameState.GAME_OVER: {
                "menu": GameState.MENU,
                "restart": GameState.RESTARTING
            },
            GameState.RESTARTING: {
                "complete": GameState.PLAYING
            }
        }
    
    def change_state(self, new_state, data=None):
        """改变游戏状态"""
        if new_state == "quit":
            return "quit"
            
        if new_state in self.state_transitions[self.current_state]:
            self.previous_state = self.current_state
            self.current_state = new_state
            return self.current_state
        else:
            print(f"无效的状态转换: {self.current_state} -> {new_state}")
            return None
    
    def push_state(self, new_state):
        """压入新状态（用于临时状态，如暂停）"""
        self.state_stack.append(self.current_state)
        self.change_state(new_state)
    
    def pop_state(self):
        """弹出状态并返回之前的状态"""
        if self.state_stack:
            previous_state = self.state_stack.pop()
            self.change_state(previous_state)
            return previous_state
        return None
    
    def get_state(self):
        """获取当前状态"""
        return self.current_state
    
    def is_state(self, state):
        """检查当前状态是否为指定状态"""
        return self.current_state == state