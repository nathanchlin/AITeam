class GameRenderer:
    """游戏渲染器"""
    def __init__(self, screen):
        self.screen = screen
        self.state_manager = GameStateManager()
        
    def render(self):
        """根据当前状态渲染游戏"""
        if self.state_manager.get_state() == GameState.MENU:
            self.render_menu()
        elif self.state_manager.get_state() == GameState.STARTING:
            self.render_starting()
        elif self.state_manager.get_state() == GameState.PLAYING:
            self.render_playing()
        elif self.state_manager.get_state() == GameState.PAUSED:
            self.render_paused()
        elif self.state_manager.get_state() == GameState.GAME_OVER:
            self.render_game_over()
        elif self.state_manager.get_state() == GameState.EXITING:
            self.render_exiting()
            
    def render_menu(self):
        """渲染菜单界面"""
        self.screen.fill((0, 0, 0))
        font = pygame.font.SysFont(None, 36)
        title = font.render("俄罗斯方块", True, (255, 255, 255))
        start = font.render("按 S 开始游戏", True, (255, 255, 255))
        quit_text = font.render("按 Q 退出游戏", True, (255, 255, 255))
        
        self.screen.blit(title, (self.screen.get_width() // 2 - title.get_width() // 2, 100))
        self.screen.blit(start, (self.screen.get_width() // 2 - start.get_width() // 2, 200))
        self.screen.blit(quit_text, (self.screen.get_width() // 2 - quit_text.get_width() // 2, 250))
        
    def render_playing(self):
        """渲染游戏进行中界面"""
        self.screen.fill((0, 0, 0))
        # 渲染游戏板
        # 渲染当前方块
        # 渲染分数等信息
        
    def render_paused(self):
        """渲染暂停界面"""
        self.render_playing()  # 先渲染游戏画面
        # 添加半透明遮罩
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        font = pygame.font.SysFont(None, 48)
        pause_text = font.render("游戏暂停", True, (255, 255, 255))
        resume_text = font.render("按 P 继续游戏", True, (255, 255, 255))
        
        self.screen.blit(pause_text, (self.screen.get_width() // 2 - pause_text.get_width() // 2, 200))
        self.screen.blit(resume_text, (self.screen.get_width() // 2 - resume_text.get_width() // 2, 250))
        
    def render_game_over(self):
        """渲染游戏结束界面"""
        self.screen.fill((0, 0, 0))
        font = pygame.font.SysFont(None, 48)
        game_over_text = font.render("游戏结束", True, (255, 255, 255))
        score_text = font.render(f"得分: {self.state_manager.score}", True, (255, 255, 255))
        restart_text = font.render("按 R 重新开始", True, (255, 255, 255))
        menu_text = font.render("按 M 返回菜单", True, (255, 255, 255))
        
        self.screen.blit(game_over_text, (self.screen.get_width() // 2 - game_over_text.get_width() // 2, 100))
        self.screen.blit(score_text, (self.screen.get_width() // 2 - score_text.get_width() // 2, 200))
        self.screen.blit(restart_text, (self.screen.get_width() // 2 - restart_text.get_width() // 2, 300))
        self.screen.blit(menu_text, (self.screen.get_width() // 2 - menu_text.get_width() // 2, 350))