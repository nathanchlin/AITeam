class Particle:
    """粒子效果类"""
    def __init__(self, x: float, y: float, color: Tuple[int, int, int]):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(2, 5)
        self.speed_x = random.uniform(-3, 3)
        self.speed_y = random.uniform(-3, 3)
        self.lifetime = random.randint(20, 40)
        self.active = True
    
    def update(self):
        """更新粒子状态"""
        self.x += self.speed_x
        self.y += self.speed_y
        self.lifetime -= 1
        self.size = max(1, self.size - 0.1)
        
        if self.lifetime <= 0:
            self.active = False
    
    def draw(self, screen):
        """绘制粒子"""
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.size))