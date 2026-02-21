class Brick:
    def __init__(self, x, y, width, height, color, hits=1):
        """
        初始化砖块
        
        参数:
            x, y: 砖块位置
            width, height: 砖块尺寸
            color: 砖块颜色
            hits: 砖块需要击中的次数
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.hits = hits
        self.max_hits = hits
        
    def hit(self):
        """
        砖块被击中，返回是否应该被移除
        
        返回:
            bool: 砖块是否应该被移除
        """
        self.hits -= 1
        return self.hits <= 0
        
    def draw(self, screen):
        """
        绘制砖块
        
        参数:
            screen: Pygame屏幕对象
        """
        # 根据剩余生命值调整颜色
        color_ratio = self.hits / self.max_hits
        color = (
            int(self.color[0] * color_ratio),
            int(self.color[1] * color_ratio),
            int(self.color[2] * color_ratio)
        )
        pygame.draw.rect(screen, color, 
                        (self.x, self.y, self.width, self.height))