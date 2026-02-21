class GameObject:
    """游戏对象基类"""
    def __init__(self, x: float, y: float, width: float, height: float, color: Tuple[int, int, int]):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.active = True
    
    def update(self):
        """更新游戏对象状态"""
        pass
    
    def draw(self, screen):
        """绘制游戏对象"""
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
    
    def get_rect(self):
        """获取游戏对象的矩形碰撞区域"""
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def is_off_screen(self):
        """检查对象是否离开屏幕"""
        return (self.x < -self.width or self.x > SCREEN_WIDTH or 
                self.y < -self.height or self.y > SCREEN_HEIGHT)