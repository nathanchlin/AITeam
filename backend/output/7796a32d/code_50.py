class GameMenu:
    def __init__(self, screen_width, screen_height, font):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font = font
        self.title_font = pygame.font.Font(None, 72)
        self.state = "main"  # main, paused, game_over
        self.buttons = []
        self.create_buttons()
    
    def create_buttons(self):
        """创建菜单按钮"""
        button_width = 300
        button_height = 50
        button_x = (self.screen_width - button_width) // 2
        
        # 主菜单按钮
        self.main_buttons = [
            Button(button_x, 200, button_width, button_height, "Start Game", self.font),
            Button(button_x, 270, button_width, button_height, "Options", self.font),
            Button(button_x, 340, button_width, button_height, "Quit", self.font)
        ]
        
        # 暂停菜单按钮
        self.pause_buttons = [
            Button(button_x, 200, button_width, button_height, "Resume", self.font),
            Button(button_x, 270, button_width, button_height, "Restart", self.font),
            Button(button_x, 340, button_width, button_height, "Main Menu", self.font)
        ]
        
        # 游戏结束菜单按钮
        self.game_over_buttons = [
            Button(button_x, 250, button_width, button_height, "Try Again", self.font),
            Button(button_x, 320, button_width, button_height, "Main Menu", self.font)
        ]
    
    def draw(self, screen):
        """绘制菜单"""
        if self.state == "main":
            self.draw_main_menu(screen)
        elif self.state == "paused":
            self.draw_pause_menu(screen)
        elif self.state == "game_over":
            self.draw_game_over_menu(screen)
    
    def draw_main_menu(self, screen):
        """绘制主菜单"""
        # 绘制标题
        title_text = self.title_font.render("是男人就下100层", True, (255, 215, 0))
        title_rect = title_text.get_rect(center=(self.screen_width // 2, 100))
        screen.blit(title_text, title_rect)
        
        # 绘制按钮
        for button in self.main_buttons:
            button.draw(screen)
    
    def draw_pause_menu(self, screen):
        """绘制暂停菜单"""
        # 绘制半透明背景
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))
        
        # 绘制标题
        title_text = self.title_font.render("PAUSED", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.screen_width // 2, 100))
        screen.blit(title_text, title_rect)
        
        # 绘制按钮
        for button in self.pause_buttons:
            button.draw(screen)
    
    def draw_game_over_menu(self, screen):
        """绘制游戏结束菜单"""
        # 绘制半透明背景
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))
        
        # 绘制标题
        title_text = self.title_font.render("GAME OVER", True, (255, 100, 100))
        title_rect = title_text.get_rect(center=(self.screen_width // 2, 100))
        screen.blit(title_text, title_rect)
        
        # 绘制分数
        score_text = self.font.render(f"Final Score: {self.final_score}", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(self.screen_width // 2, 180))
        screen.blit(score_text, score_rect)
        
        # 绘制按钮
        for button in self.game_over_buttons:
            button.draw(screen)
    
    def handle_event(self, event):
        """处理菜单事件"""
        if event.type == pygame.MOUSEMOTION:
            if self.state == "main":
                for button in self.main_buttons:
                    button.hover = button.rect.collidepoint(event.pos)
            elif self.state == "paused":
                for button in self.pause_buttons:
                    button.hover = button.rect.collidepoint(event.pos)
            elif self.state == "game_over":
                for button in self.game_over_buttons:
                    button.hover = button.rect.collidepoint(event.pos)
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.state == "main":
                for i, button in enumerate(self.main_buttons):
                    if button.rect.collidepoint(event.pos):
                        if i == 0:  # Start Game
                            return "start_game"
                        elif i == 1:  # Options
                            return "options"
                        elif i == 2:  # Quit
                            return "quit"
            elif self.state == "paused":
                for i, button in enumerate(self.pause_buttons):
                    if button.rect.collidepoint(event.pos):
                        if i == 0:  # Resume
                            return "resume"
                        elif i == 1:  # Restart
                            return "restart"
                        elif i == 2:  # Main Menu
                            return "main_menu"
            elif self.state == "game_over":
                for i, button in enumerate(self.game_over_buttons):
                    if button.rect.collidepoint(event.pos):
                        if i == 0:  # Try Again
                            return "restart"
                        elif i == 1:  # Main Menu
                            return "main_menu"
        
        return None