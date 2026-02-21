class Bullet:
    def __init__(self, x, y, angle, color=(255, 255, 0), speed=5, damage=10):
        """
        初始化子弹
        
        参数:
            x, y: 子弹初始位置
            angle: 子弹飞行角度(度)
            color: 子弹颜色
            speed: 子弹速度
            damage: 子弹伤害值
        """
        self.x = x
        self.y = y
        self.angle = angle
        self.color = color
        self.speed = speed
        self.damage = damage
        self.radius = 3
        self.active = True
    
    def update(self):
        """更新子弹位置"""
        if not self.active:
            return
            
        rad = math.radians(self.angle)
        self.x += self.speed * math.cos(rad)
        self.y -= self.speed * math.sin(rad)
    
    def draw(self, screen):
        """绘制子弹"""
        if self.active:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
    
    def get_rect(self):
        """获取子弹的矩形碰撞区域"""
        return pygame.Rect(self.x - self.radius, self.y - self.radius, 
                          self.radius * 2, self.radius * 2)