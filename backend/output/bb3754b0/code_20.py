class VisualEffects:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.particle_system = ParticleSystem()
        self.screen_shake = 0
        self.flash_alpha = 0
        
    def add_jump_effect(self, x, y):
        """添加跳跃特效"""
        self.particle_system.emit(x, y, 15, (100, 200, 255))
    
    def add_collision_effect(self, x, y):
        """添加碰撞特效"""
        self.particle_system.emit(x, y, 30, (255, 50, 50))
        self.screen_shake = 0.3
        self.flash_alpha = 100
    
    def add_score_effect(self, x, y):
        """添加得分特效"""
        self.particle_system.emit(x, y, 20, (255, 215, 0))
    
    def update(self, dt):
        """更新所有视觉效果"""
        self.particle_system.update(dt)
        
        if self.screen_shake > 0:
            self.screen_shake -= dt
        
        if self.flash_alpha > 0:
            self.flash_alpha -= dt * 200
    
    def draw(self, screen):
        """绘制所有视觉效果"""
        # 绘制粒子效果
        self.particle_system.draw(screen)
        
        # 绘制屏幕震动效果
        if self.screen_shake > 0:
            shake_x = random.randint(-int(self.screen_shake * 10), int(self.screen_shake * 10))
            shake_y = random.randint(-int(self.screen_shake * 10), int(self.screen_shake * 10))
            screen.blit(screen, (shake_x, shake_y))
        
        # 绘制闪光效果
        if self.flash_alpha > 0:
            flash_surface = pygame.Surface((self.screen_width, self.screen_height))
            flash_surface.set_alpha(int(self.flash_alpha))
            flash_surface.fill((255, 255, 255))
            screen.blit(flash_surface, (0, 0))