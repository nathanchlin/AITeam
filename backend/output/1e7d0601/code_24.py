class Bullet:
    def __init__(self, x, y, dx, dy, damage=10, speed=10, is_laser=False):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.damage = damage
        self.speed = speed * (2 if is_laser else 1)  # 激光速度更快
        self.width = 4 if not is_laser else 6
        self.height = 12 if not is_laser else 20
        self.is_laser = is_laser
        self.active = True
        
    def update(self):
        """更新子弹位置"""
        self.x += self.dx * self.speed
        self.y += self.dy * self.speed
        
    def draw(self, screen):
        """绘制子弹"""
        if not self.active:
            return
            
        if self.is_laser:
            # 激光效果
            pygame.draw.rect(screen, (0, 255, 255), 
                            (self.x - self.width // 2, self.y - self.height // 2, 
                             self.width, self.height))
            # 发光效果
            pygame.draw.rect(screen, (100, 255, 255), 
                            (self.x - self.width // 2 - 1, self.y - self.height // 2 - 1, 
                             self.width + 2, self.height + 2), 1)
        else:
            # 普通子弹
            pygame.draw.rect(screen, (255, 255, 0), 
                            (self.x - self.width // 2, self.y - self.height // 2, 
                             self.width, self.height))
            
    def is_off_screen(self, screen_width, screen_height):
        """检查子弹是否离开屏幕"""
        return (self.x < 0 or self.x > screen_width or 
                self.y < 0 or self.y > screen_height)