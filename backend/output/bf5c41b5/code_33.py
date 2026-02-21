class Game:
    def __init__(self):
        self.state_manager = GameStateManager()
        self.score = 0
        self.lives = 3
        self.level = 1
        self.paddle = Paddle()
        self.ball = Ball()
        self.bricks = []
        self.clock = pygame.time.Clock()
        self.running = True
        
    def handle_events(self):
        """处理游戏事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            if self.state_manager.is_state(GameState.MENU):
                self.handle_menu_events(event)
            elif self.state_manager.is_state(GameState.PLAYING):
                self.handle_playing_events(event)
            elif self.state_manager.is_state(GameState.PAUSED):
                self.handle_paused_events(event)
            elif self.state_manager.is_state(GameState.GAME_OVER):
                self.handle_game_over_events(event)
            elif self.state_manager.is_state(GameState.LEVEL_COMPLETE):
                self.handle_level_complete_events(event)
            elif self.state_manager.is_state(GameState.SETTINGS):
                self.handle_settings_events(event)
    
    def handle_menu_events(self, event):
        """处理主菜单事件"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:  # 开始游戏
                self.state_manager.change_state(GameState.PLAYING, "start")
                self.reset_level()
            elif event.key == pygame.K_s:  # 设置
                self.state_manager.change_state(GameState.SETTINGS, "settings")
            elif event.key == pygame.K_q:  # 退出
                self.running = False
    
    def handle_playing_events(self, event):
        """处理游戏中事件"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:  # 暂停
                self.state_manager.change_state(GameState.PAUSED, "pause")
            elif event.key == pygame.K_LEFT:
                self.paddle.move_left()
            elif event.key == pygame.K_RIGHT:
                self.paddle.move_right()
        elif event.type == pygame.KEYUP:
            if event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
                self.paddle.stop()
    
    def handle_paused_events(self, event):
        """处理暂停事件"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:  # 继续游戏
                self.state_manager.change_state(GameState.PLAYING, "resume")
            elif event.key == pygame.K_r:  # 重新开始
                self.state_manager.change_state(GameState.PLAYING, "restart")
                self.reset_level()
            elif event.key == pygame.K_m:  # 返回菜单
                self.state_manager.change_state(GameState.MENU, "menu")
    
    def handle_game_over_events(self, event):
        """处理游戏结束事件"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:  # 重新开始
                self.state_manager.change_state(GameState.PLAYING, "restart")
                self.reset_game()
            elif event.key == pygame.K_m:  # 返回菜单
                self.state_manager.change_state(GameState.MENU, "menu")
    
    def handle_level_complete_events(self, event):
        """处理关卡完成事件"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_n:  # 下一关
                self.state_manager.change_state(GameState.PLAYING, "next_level")
                self.next_level()
            elif event.key == pygame.K_m:  # 返回菜单
                self.state_manager.change_state(GameState.MENU, "menu")
    
    def handle_settings_events(self, event):
        """处理设置事件"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:  # 返回菜单
                self.state_manager.change_state(GameState.MENU, "back")
    
    def update(self):
        """更新游戏逻辑"""
        if self.state_manager.is_state(GameState.PLAYING):
            self.update_game()
    
    def update_game(self):
        """更新游戏状态"""
        self.paddle.update()
        self.ball.update()
        
        # 检测球与挡板碰撞
        if self.ball.collides_with_paddle(self.paddle):
            self.ball.bounce_off_paddle(self.paddle)
        
        # 检测球与砖块碰撞
        for brick in self.bricks[:]:
            if self.ball.collides_with_brick(brick):
                self.ball.bounce_off_brick(brick)
                self.bricks.remove(brick)
                self.score += 10
                
                # 检查是否完成关卡
                if not self.bricks:
                    self.state_manager.change_state(GameState.LEVEL_COMPLETE, "level_complete")
        
        # 检测球是否掉落
        if self.ball.y > SCREEN_HEIGHT:
            self.lives -= 1
            if self.lives <= 0:
                self.state_manager.change_state(GameState.GAME_OVER, "game_over")
            else:
                self.reset_ball()
    
    def render(self):
        """渲染游戏画面"""
        screen.fill(BLACK)
        
        if self.state_manager.is_state(GameState.MENU):
            self.render_menu()
        elif self.state_manager.is_state(GameState.PLAYING):
            self.render_game()
        elif self.state_manager.is_state(GameState.PAUSED):
            self.render_game()
            self.render_paused_overlay()
        elif self.state_manager.is_state(GameState.GAME_OVER):
            self.render_game_over()
        elif self.state_manager.is_state(GameState.LEVEL_COMPLETE):
            self.render_level_complete()
        elif self.state_manager.is_state(GameState.SETTINGS):
            self.render_settings()
        
        pygame.display.flip()
    
    def render_menu(self):
        """渲染主菜单"""
        font = pygame.font.SysFont(None, 36)
        title = font.render("打砖块游戏", True, WHITE)
        start = font.render("按 Enter 开始游戏", True, WHITE)
        settings = font.render("按 S 进入设置", True, WHITE)
        quit = font.render("按 Q 退出游戏", True, WHITE)
        
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))
        screen.blit(start, (SCREEN_WIDTH//2 - start.get_width()//2, 200))
        screen.blit(settings, (SCREEN_WIDTH//2 - settings.get_width()//2, 250))
        screen.blit(quit, (SCREEN_WIDTH//2 - quit.get_width()//2, 300))
    
    def render_game(self):
        """渲染游戏画面"""
        self.paddle.draw(screen)
        self.ball.draw(screen)
        for brick in self.bricks:
            brick.draw(screen)
        
        # 显示分数和生命值
        font = pygame.font.SysFont(None, 24)
        score_text = font.render(f"分数: {self.score}", True, WHITE)
        lives_text = font.render(f"生命: {self.lives}", True, WHITE)
        level_text = font.render(f"关卡: {self.level}", True, WHITE)
        
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (SCREEN_WIDTH - 80, 10))
        screen.blit(level_text, (SCREEN_WIDTH//2 - level_text.get_width()//2, 10))
    
    def render_paused_overlay(self):
        """渲染暂停覆盖层"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))
        
        font = pygame.font.SysFont(None, 48)
        paused = font.render("游戏暂停", True, WHITE)
        resume = font.render("按 P 继续游戏", True, WHITE)
        restart = font.render("按 R 重新开始", True, WHITE)
        menu = font.render("按 M 返回菜单", True, WHITE)
        
        screen.blit(paused, (SCREEN_WIDTH//2 - paused.get_width()//2, 150))
        screen.blit(resume, (SCREEN_WIDTH//2 - resume.get_width()//2, 220))
        screen.blit(restart, (SCREEN_WIDTH//2 - restart.get_width()//2, 270))
        screen.blit(menu, (SCREEN_WIDTH//2 - menu.get_width()//2, 320))
    
    def render_game_over(self):
        """渲染游戏结束画面"""
        font = pygame.font.SysFont(None, 48)
        game_over = font.render("游戏结束", True, WHITE)
        score = font.render(f"最终分数: {self.score}", True, WHITE)
        restart = font.render("按 R 重新开始", True, WHITE)
        menu = font.render("按 M 返回菜单", True, WHITE)
        
        screen.blit(game_over, (SCREEN_WIDTH//2 - game_over.get_width()//2, 150))
        screen.blit(score, (SCREEN_WIDTH//2 - score.get_width()//2, 220))
        screen.blit(restart, (SCREEN_WIDTH//2 - restart.get_width()//2, 270))
        screen.blit(menu, (SCREEN_WIDTH//2 - menu.get_width()//2, 320))
    
    def render_level_complete(self):
        """渲染关卡完成画面"""
        font = pygame.font.SysFont(None, 48)
        complete = font.render("关卡完成!", True, WHITE)
        score = font.render(f"当前分数: {self.score}", True, WHITE)
        next_level = font.render("按 N 下一关", True, WHITE)
        menu = font.render("按 M 返回菜单", True, WHITE)
        
        screen.blit(complete, (SCREEN_WIDTH//2 - complete.get_width()//2, 150))
        screen.blit(score, (SCREEN_WIDTH//2 - score.get_width()//2, 220))
        screen.blit(next_level, (SCREEN_WIDTH//2 - next_level.get_width()//2, 270))
        screen.blit(menu, (SCREEN_WIDTH//2 - menu.get_width()//2, 320))
    
    def render_settings(self):
        """渲染设置画面"""
        font = pygame.font.SysFont(None, 36)
        title = font.render("设置", True, WHITE)
        back = font.render("按 ESC 返回菜单", True, WHITE)
        
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))
        screen.blit(back, (SCREEN_WIDTH//2 - back.get_width()//2, 200))
    
    def reset_level(self):
        """重置当前关卡"""
        self.paddle.reset()
        self.reset_ball()
        self.create_bricks()
    
    def reset_game(self):
        """重置整个游戏"""
        self.score = 0
        self.lives = 3
        self.level = 1
        self.reset_level()
    
    def reset_ball(self):
        """重置球的位置"""
        self.ball.reset()
    
    def next_level(self):
        """进入下一关"""
        self.level += 1
        self.reset_level()
    
    def create_bricks(self):
        """创建砖块"""
        self.bricks = []
        rows = 5
        cols = 10
        brick_width = 70
        brick_height = 20
        padding = 5
        offset_x = (SCREEN_WIDTH - (cols * (brick_width + padding))) // 2
        offset_y = 60
        
        for row in range(rows):
            for col in range(cols):
                x = offset_x + col * (brick_width + padding)
                y = offset_y + row * (brick_height + padding)
                color = (255 - row * 40, 100 + row * 30, 150)
                self.bricks.append(Brick(x, y, brick_width, brick_height, color))
    
    def run(self):
        """游戏主循环"""
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(60)