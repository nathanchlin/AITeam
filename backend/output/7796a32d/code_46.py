class PlayerEffects:
    def __init__(self):
        self.dust_particles = []
        self.footstep_effect = None
        self.power_up_effects = []
    
    def create_landing_effect(self, x, y):
        """创建落地时的灰尘效果"""
        for _ in range(20):
            particle = {
                'x': x + random.randint(-10, 10),
                'y': y,
                'vx': random.uniform(-2, 2),
                'vy': random.uniform(-5, -2),
                'size': random.randint(2, 5),
                'lifetime': 20,
                'color': (139, 90, 43)  # 棕色
            }
            self.dust_particles.append(particle)
    
    def update_particles(self):
        """更新所有粒子效果"""
        for particle in self.dust_particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vy'] += 0.5  # 重力
            particle['lifetime'] -= 1
            
            if particle['lifetime'] <= 0:
                self.dust_particles.remove(particle)
    
    def draw_particles(self, screen):
        """绘制所有粒子效果"""
        for particle in self.dust_particles:
            alpha = particle['lifetime'] / 20
            size = int(particle['size'] * alpha)
            if size > 0:
                pygame.draw.circle(screen, particle['color'], 
                                 (int(particle['x']), int(particle['y'])), size)