class Player(GameObject):
    """玩家飞船类"""
    def __init__(self, x, y):
        super().__init__(x, y)
        self.width = 40
        self.height = 40
        self.speed = GameConfig.PLAYER_SPEED
        self.color = (0, 255, 0)  # 绿色飞船
    
    def update(self):
        """更新玩家位置"""
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < GameConfig.SCREEN_WIDTH - self.width:
            self.x += self.speed
        if keys[pygame.K_UP] and self.y > 0:
            self.y -= self.speed
        if keys[pygame.K_DOWN] and self.y < GameConfig.SCREEN_HEIGHT - self.height:
            self.y += self.speed
    
    def draw(self, screen):
        """绘制玩家飞船"""
        # 绘制三角形飞船
        points = [
            (self.x + self.width // 2, self.y),
            (self.x, self.y + self.height),
            (self.x + self.width, self.y + self.height)
        ]
        pygame.draw.polygon(screen, self.color, points)
    
    def get_rect(self):
        """获取玩家碰撞矩形"""
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Bullet(GameObject):
    """子弹类"""
    def __init__(self, x, y):
        super().__init__(x, y)
        self.width = 4
        self.height = 10
        self.speed = GameConfig.BULLET_SPEED
        self.color = (255, 255, 0)  # 黄色子弹
    
    def update(self):
        """更新子弹位置"""
        self.y -= self.speed
        
        # 如果子弹超出屏幕，标记为非活动
        if self.y < -self.height:
            self.active = False
    
    def draw(self, screen):
        """绘制子弹"""
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
    
    def get_rect(self):
        """获取子弹碰撞矩形"""
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Asteroid(GameObject):
    """陨石类"""
    def __init__(self, x, y, speed):
        super().__init__(x, y)
        self.radius = random.randint(15, 30)
        self.speed = speed
        self.rotation = 0
        self.rotation_speed = random.uniform(-2, 2)
        self.color = (150, 75, 0)  # 棕色陨石
    
    def update(self):
        """更新陨石位置和旋转"""
        self.y += self.speed
        self.rotation += self.rotation_speed
        
        # 如果陨石超出屏幕，标记为非活动
        if self.y > GameConfig.SCREEN_HEIGHT + self.radius:
            self.active = False
    
    def draw(self, screen):
        """绘制陨石"""
        # 绘制不规则形状的陨石
        points = []
        num_points = 8
        for i in range(num_points):
            angle = (2 * math.pi * i / num_points) + math.radians(self.rotation)
            r = self.radius + random.randint(-5, 5)
            x = self.x + r * math.cos(angle)
            y = self.y + r * math.sin(angle)
            points.append((x, y))
        
        pygame.draw.polygon(screen, self.color, points)
    
    def get_rect(self):
        """获取陨石碰撞矩形（使用圆形碰撞检测）"""
        return pygame.Rect(self.x - self.radius, self.y - self.radius, 
                          self.radius * 2, self.radius * 2)