class GameStateManager:
    def __init__(self):
        self.current_state = GameState.MENU
        self.state_stack = []
        self.state_transitions = {}
    
    def change_state(self, new_state):
        """切换游戏状态"""
        # 保存当前状态到堆栈
        self.state_stack.append(self.current_state)
        self.current_state = new_state
        # 触发状态切换事件
        EventSystem.emit("state_changed", {"from": self.state_stack[-1], "to": new_state})
    
    def revert_state(self):
        """返回上一个状态"""
        if self.state_stack:
            self.current_state = self.state_stack.pop()
            EventSystem.emit("state_changed", {"from": self.current_state, "to": self.state_stack[-1] if self.state_stack else None})
    
    def update(self, delta_time):
        """更新当前状态逻辑"""
        if self.current_state == GameState.PLAYING:
            # 游戏进行中的逻辑
            pass
        # 其他状态的更新逻辑...