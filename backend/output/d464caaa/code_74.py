class GameRenderer:
    def __init__(self):
        self.dirty_rects = []
        self.last_frame_state = None
    
    def mark_dirty(self, region):
        """标记需要重绘的区域"""
        self.dirty_rects.append(region)
    
    def render(self, game_state):
        """仅渲染脏区域"""
        if self.last_frame_state is None:
            # 完全重绘
            self.full_render(game_state)
        else:
            # 仅渲染脏区域
            for region in self.dirty_rects:
                self.partial_render(game_state, region)
        
        self.dirty_rects.clear()
        self.last_frame_state = game_state