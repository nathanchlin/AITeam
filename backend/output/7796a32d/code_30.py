class GameStateManager:
    def __init__(self):
        self.current_state = GameState.MENU
        self.previous_state = None
        self.state_stack = []
        self.state_change_callbacks = {}
        
    def change_state(self, new_state, *args, **kwargs):
        """切换游戏状态"""
        if self.current_state == new_state:
            return
            
        # 保存当前状态到历史记录
        self.previous_state = self.current_state
        
        # 如果是新状态被压栈，则保存当前状态
        if kwargs.get('push', False):
            self.state_stack.append(self.current_state)
            
        # 调用当前状态的退出回调
        if self.current_state in self.state_change_callbacks:
            self.state_change_callbacks[self.current_state].on_exit()
            
        # 更新当前状态
        old_state = self.current_state
        self.current_state = new_state
        
        # 调用新状态的进入回调
        if self.current_state in self.state_change_callbacks:
            self.state_change_callbacks[self.current_state].on_enter(old_state, *args, **kwargs)
            
    def revert_state(self):
        """恢复到上一个状态"""
        if self.state_stack:
            previous_state = self.state_stack.pop()
            self.change_state(previous_state)
            
    def add_state_callback(self, state, callback):
        """为特定状态添加回调"""
        self.state_change_callbacks[state] = callback
        
    def is_state(self, state):
        """检查当前是否处于指定状态"""
        return self.current_state == state
        
    def get_current_state(self):
        """获取当前状态"""
        return self.current_state