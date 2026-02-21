class Particle:
    """粒子效果类"""
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-3, -1)
        self.lifetime = 30
        self.size = random.randint(2, 5)
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1  # 重力效果
        self.lifetime -= 1
        self.size = max(1, self.size - 0.1)
        
    def draw(self, screen):
        if self.lifetime > 0:
            alpha = self.lifetime / 30
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.size))

class ParticleSystem:
    """粒子系统管理器"""
    def __init__(self):
        self.particles = []
        
    def add_particles(self, x, y, color, count=10):
        """添加粒子效果"""
        for _ in range(count):
            self.particles.append(Particle(x, y, color))
            
    def update(self):
        """更新所有粒子"""
        self.particles = [p for p in self.particles if p.lifetime > 0]
        for particle in self.particles:
            particle.update()
            
    def draw(self, screen):
        """绘制所有粒子"""
        for particle in self.particles:
            particle.draw(screen)