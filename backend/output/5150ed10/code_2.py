class Bullet:
    def __init__(self, x, y):
        """初始化子弹"""
        self.x = x
        self.y = y
        self.width = 4
        self.height = 10
        self.speed = 10
        self.active = True
        
    def update(self):
        """更新子弹位置"""
        self.y -= self.speed
        # 如果子弹飞出屏幕，标记为非活动
        if self.y < -self.height:
            self.active = False
            
    def draw(self, screen):
        """绘制子弹"""
        if self.active:
            pygame.draw.rect(screen, (255, 255, 0), (self.x, self.y, self.width, self.height))
            
    def get_rect(self):
        """获取子弹的矩形碰撞区域"""
        return pygame.Rect(self.x, self.y, self.width, self.height)