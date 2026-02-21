class EffectManager:
    def __init__(self):
        self.player_effects = PlayerEffects()
        self.platform_effects = PlatformEffects()
        self.screen_shake = 0
        self.screen_shake_intensity = 0
    
    def add_screen_shake(self, intensity, duration):
        """添加屏幕震动效果"""
        self.screen_shake_intensity = intensity
        self.screen_shake_duration = duration
    
    def update(self):
        """更新所有效果"""
        self.player_effects.update_particles()
        self.platform_effects.update_breaking_platforms()
        
        # 更新屏幕震动
        if self.screen_shake > 0:
            self.screen_shake -= 1
            if self.screen_shake <= 0:
                self.screen_shake_intensity = 0
    
    def draw(self, screen):
        """绘制所有效果"""
        self.player_effects.draw_particles(screen)
        self.platform_effects.draw_breaking_platforms(screen)
        
        # 应用屏幕震动
        if self.screen_shake > 0:
            shake_x = random.randint(-self.screen_shake_intensity, self.screen_shake_intensity)
            shake_y = random.randint(-self.screen_shake_intensity, self.screen_shake_intensity)
            screen.blit(screen, (shake_x, shake_y))
    
    def get_shake_offset(self):
        """获取当前屏幕震动偏移量"""
        if self.screen_shake > 0:
            return (
                random.randint(-self.screen_shake_intensity, self.screen_shake_intensity),
                random.randint(-self.screen_shake_intensity, self.screen_shake_intensity)
            )
        return (0, 0)