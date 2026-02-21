class BallTrail:
    """球的拖尾效果"""
    def __init__(self, max_length=10):
        self.positions = []
        self.max_length = max_length
        
    def update(self, ball_pos):
        """更新拖尾位置"""
        self.positions.append(ball_pos)
        if len(self.positions) > self.max_length:
            self.positions.pop(0)
            
    def draw(self, screen, ball_color):
        """绘制拖尾效果"""
        for i, pos in enumerate(self.positions):
            alpha = i / len(self.positions)
            size = int(5 * alpha)
            if size > 0:
                color = tuple(int(c * alpha) for c in ball_color)
                pygame.draw.circle(screen, color, (int(pos[0]), int(pos[1])), size)