class UI:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)
        self.score = 0
        self.coins = 0
        self.health = 100
        self.combo = 0
        
    def update_score(self, points):
        self.score += points
        self.combo += 1
        
    def reset_combo(self):
        self.combo = 0
        
    def collect_coin(self):
        self.coins += 1
        
    def take_damage(self, amount):
        self.health = max(0, self.health - amount)
        
    def draw(self, screen):
        # 分数显示
        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
        
        # 金币显示
        coin_text = self.font.render(f"Coins: {self.coins}", True, (255, 215, 0))
        screen.blit(coin_text, (10, 50))
        
        # 生命值条
        pygame.draw.rect(screen, (100, 100, 100), (10, 90, 200, 20))
        pygame.draw.rect(screen, (0, 255, 0), (10, 90, int(200 * self.health / 100), 20))
        
        # 连击显示
        if self.combo > 1:
            combo_text = self.big_font.render(f"{self.combo}x COMBO!", True, (255, 100, 100))
            combo_rect = combo_text.get_rect(center=(self.screen_width // 2, 100))
            screen.blit(combo_text, combo_rect)
            
        # 游戏结束画面
        if self.health <= 0:
            game_over_text = self.big_font.render("GAME OVER", True, (255, 0, 0))
            game_over_rect = game_over_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            screen.blit(game_over_text, game_over_rect)
            
            final_score_text = self.font.render(f"Final Score: {self.score}", True, (255, 255, 255))
            final_score_rect = final_score_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 50))
            screen.blit(final_score_text, final_score_rect)