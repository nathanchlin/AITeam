class GameHUD:
    def __init__(self, screen):
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        
        # 字体
        self.font = pygame.font.Font("assets/fonts/retro.ttf", 24)
        self.big_font = pygame.font.Font("assets/fonts/retro.ttf", 36)
        
        # 生命值系统
        self.max_lives = 3
        self.lives = self.max_lives
        
        # 得分系统
        self.score = 0
        self.high_score = 0
        
        # 武器系统
        self.weapon_level = 1
        self.power_ups = []
        
        # 游戏状态
        self.game_over = False
        self.paused = False
        
    def update(self, player, enemies, powerups):
        # 更新生命值
        self.lives = player.lives
        
        # 更新得分
        self.score = player.score
        
        # 更新武器等级
        self.weapon_level = player.weapon_level
        
        # 更新道具
        self.power_ups = powerups
        
    def draw(self):
        # 绘制得分
        score_text = self.font.render(f"SCORE: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))
        
        # 绘制最高分
        high_score_text = self.font.render(f"HIGH: {self.high_score}", True, (255, 255, 255))
        self.screen.blit(high_score_text, (10, 40))
        
        # 绘制生命值
        for i in range(self.lives):
            plane_img = pygame.image.load("assets/player_plane_small.png")
            self.screen.blit(plane_img, (self.width - 40 - i * 35, 10))
            
        # 绘制武器等级
        weapon_text = self.font.render(f"WEAPON: {self.weapon_level}", True, (255, 255, 255))
        self.screen.blit(weapon_text, (10, 70))
        
        # 绘制道具状态
        y_offset = 100
        for powerup in self.power_ups:
            powerup_text = self.font.render(f"{powerup.name}: {powerup.duration}s", True, (255, 255, 0))
            self.screen.blit(powerup_text, (10, y_offset))
            y_offset += 30
            
        # 如果游戏暂停，显示暂停信息
        if self.paused:
            pause_text = self.big_font.render("PAUSED", True, (255, 255, 0))
            pause_rect = pause_text.get_rect(center=(self.width // 2, self.height // 2))
            self.screen.blit(pause_text, pause_rect)
            
            continue_text = self.font.render("Press P to continue", True, (255, 255, 255))
            continue_rect = continue_text.get_rect(center=(self.width // 2, self.height // 2 + 50))
            self.screen.blit(continue_text, continue_rect)
            
        # 如果游戏结束，显示游戏结束信息
        if self.game_over:
            game_over_text = self.big_font.render("GAME OVER", True, (255, 0, 0))
            game_over_rect = game_over_text.get_rect(center=(self.width // 2, self.height // 2 - 50))
            self.screen.blit(game_over_text, game_over_rect)
            
            score_text = self.big_font.render(f"Final Score: {self.score}", True, (255, 255, 255))
            score_rect = score_text.get_rect(center=(self.width // 2, self.height // 2))
            self.screen.blit(score_text, score_rect)
            
            restart_text = self.font.render("Press SPACE to return to menu", True, (255, 255, 255))
            restart_rect = restart_text.get_rect(center=(self.width // 2, self.height // 2 + 50))
            self.screen.blit(restart_text, restart_rect)