class Brick:
    def __init__(self, x, y, width, height, color, hits=1, points=10):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.hits = hits  # 砖块需要被击中的次数
        self.points = points  # 消除该砖块获得的分数
        self.is_active = True  # 砖块是否还存在
        
    def hit(self):
        """砖块被击中，减少生命值"""
        self.hits -= 1
        if self.hits <= 0:
            self.is_active = False
            return self.points  # 返回得分
        return 0
    
    def draw(self, surface):
        """绘制砖块"""
        if self.is_active:
            pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))
            pygame.draw.rect(surface, (0, 0, 0), (self.x, self.y, self.width, self.height), 2)  # 边框
    
    def get_rect(self):
        """获取砖块的矩形区域，用于碰撞检测"""
        return pygame.Rect(self.x, self.y, self.width, self.height)