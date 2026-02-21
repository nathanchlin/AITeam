class Paddle:
    def __init__(self, x, y, width, height, speed):
        """
        初始化挡板
        
        参数:
            x, y: 挡板位置
            width, height: 挡板尺寸
            speed: 挡板移动速度
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = speed
        self.moving_left = False
        self.moving_right = False
        
    def update(self, dt, width):
        """
        更新挡板位置
        
        参数:
            dt: 时间增量(秒)
            width: 屏幕宽度，用于边界检查
        """
        if self.moving_left:
            self.x -= self.speed * dt
            if self.x < 0:
                self.x = 0
                
        if self.moving_right:
            self.x += self.speed * dt
            if self.x + self.width > width:
                self.x = width - self.width
                
    def draw(self, screen):
        """
        绘制挡板
        
        参数:
            screen: Pygame屏幕对象
        """
        pygame.draw.rect(screen, (255, 255, 255), 
                        (self.x, self.y, self.width, self.height))