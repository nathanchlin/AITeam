class GameObject:
    """游戏对象基类"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.active = True
    
    def update(self):
        """更新游戏对象状态"""
        pass
    
    def draw(self, screen):
        """绘制游戏对象"""
        pass
    
    def get_rect(self):
        """获取对象的碰撞矩形"""
        return pygame.Rect(self.x, self.y, 0, 0)  # 子类应重写此方法

class GameEngine:
    """游戏引擎核心类"""
    def __init__(self):
        self.screen = pygame.display.set_mode((GameConfig.SCREEN_WIDTH, GameConfig.SCREEN_HEIGHT))
        pygame.display.set_caption("太空射击游戏")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = GameState.MENU
        self.game_objects = []
        self.score = 0
        self.font = pygame.font.SysFont(None, 36)
        
        # 玩家对象
        self.player = None
        
        # 陨石生成计时器
        self.asteroid_spawn_timer = 0
        self.asteroid_spawn_delay = 60  # 初始生成延迟（帧数）
    
    def handle_events(self):
        """处理游戏事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if self.state == GameState.MENU:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.start_game()
            
            elif self.state == GameState.PLAYING:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        self.state = GameState.PAUSED
                    elif event.key == pygame.K_SPACE:
                        self.shoot_bullet()
            
            elif self.state == GameState.PAUSED:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        self.state = GameState.PLAYING
            
            elif self.state == GameState.GAME_OVER:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.start_game()
    
    def start_game(self):
        """开始新游戏"""
        self.state = GameState.PLAYING
        self.score = 0
        self.game_objects.clear()
        
        # 创建玩家
        self.player = Player(GameConfig.SCREEN_WIDTH // 2, GameConfig.SCREEN_HEIGHT - 50)
        self.game_objects.append(self.player)
        
        # 重置游戏参数
        self.asteroid_spawn_timer = 0
        self.asteroid_spawn_delay = 60
    
    def shoot_bullet(self):
        """发射子弹"""
        if self.player:
            bullet = Bullet(self.player.x, self.player.y - 20)
            self.game_objects.append(bullet)
    
    def spawn_asteroid(self):
        """生成陨石"""
        x = random.randint(0, GameConfig.SCREEN_WIDTH)
        y = -30
        speed = random.uniform(GameConfig.ASTEROID_MIN_SPEED, GameConfig.ASTEROID_MAX_SPEED)
        asteroid = Asteroid(x, y, speed)
        self.game_objects.append(asteroid)
    
    def update(self):
        """更新游戏状态"""
        if self.state == GameState.PLAYING:
            # 更新所有游戏对象
            for obj in self.game_objects[:]:
                obj.update()
                if not obj.active:
                    self.game_objects.remove(obj)
            
            # 生成陨石
            self.asteroid_spawn_timer += 1
            if self.asteroid_spawn_timer >= self.asteroid_spawn_delay:
                self.spawn_asteroid()
                self.asteroid_spawn_timer = 0
                
                # 随着分数增加，加快陨石生成速度
                self.asteroid_spawn_delay = max(20, 60 - self.score // 10)
            
            # 检测碰撞
            self.check_collisions()
            
            # 检查游戏结束条件
            if self.player and not self.player.active:
                self.state = GameState.GAME_OVER
    
    def check_collisions(self):
        """检测游戏对象之间的碰撞"""
        # 子弹与陨石碰撞
        bullets = [obj for obj in self.game_objects if isinstance(obj, Bullet)]
        asteroids = [obj for obj in self.game_objects if isinstance(obj, Asteroid)]
        
        for bullet in bullets:
            for asteroid in asteroids:
                if bullet.get_rect().colliderect(asteroid.get_rect()):
                    bullet.active = False
                    asteroid.active = False
                    self.score += 10
        
        # 玩家与陨石碰撞
        if self.player:
            for asteroid in asteroids:
                if self.player.get_rect().colliderect(asteroid.get_rect()):
                    self.player.active = False
    
    def draw(self):
        """绘制游戏画面"""
        self.screen.fill(GameConfig.BACKGROUND_COLOR)
        
        if self.state == GameState.MENU:
            self.draw_menu()
        elif self.state == GameState.PLAYING:
            # 绘制所有游戏对象
            for obj in self.game_objects:
                obj.draw(self.screen)
            
            # 绘制分数
            score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
            self.screen.blit(score_text, (10, 10))
            
            # 绘制提示
            pause_text = self.font.render("Press P to pause", True, (255, 255, 255))
            self.screen.blit(pause_text, (GameConfig.SCREEN_WIDTH - 200, 10))
            
        elif self.state == GameState.PAUSED:
            # 绘制游戏对象（暂停状态）
            for obj in self.game_objects:
                obj.draw(self.screen)
            
            # 绘制暂停信息
            pause_text = self.font.render("PAUSED - Press P to continue", True, (255, 255, 255))
            text_rect = pause_text.get_rect(center=(GameConfig.SCREEN_WIDTH // 2, GameConfig.SCREEN_HEIGHT // 2))
            self.screen.blit(pause_text, text_rect)
            
        elif self.state == GameState.GAME_OVER:
            self.draw_game_over()
        
        pygame.display.flip()
    
    def draw_menu(self):
        """绘制主菜单"""
        title_text = self.font.render("SPACE SHOOTER", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(GameConfig.SCREEN_WIDTH // 2, 200))
        self.screen.blit(title_text, title_rect)
        
        start_text = self.font.render("Press SPACE to start", True, (255, 255, 255))
        start_rect = start_text.get_rect(center=(GameConfig.SCREEN_WIDTH // 2, 300))
        self.screen.blit(start_text, start_rect)
        
        controls_text = self.font.render("Controls: Arrow keys to move, SPACE to shoot", True, (255, 255, 255))
        controls_rect = controls_text.get_rect(center=(GameConfig.SCREEN_WIDTH // 2, 400))
        self.screen.blit(controls_text, controls_rect)
    
    def draw_game_over(self):
        """绘制游戏结束画面"""
        game_over_text = self.font.render("GAME OVER", True, (255, 0, 0))
        game_over_rect = game_over_text.get_rect(center=(GameConfig.SCREEN_WIDTH // 2, 200))
        self.screen.blit(game_over_text, game_over_rect)
        
        score_text = self.font.render(f"Final Score: {self.score}", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(GameConfig.SCREEN_WIDTH // 2, 300))
        self.screen.blit(score_text, score_rect)
        
        restart_text = self.font.render("Press SPACE to restart", True, (255, 255, 255))
        restart_rect = restart_text.get_rect(center=(GameConfig.SCREEN_WIDTH // 2, 400))
        self.screen.blit(restart_text, restart_rect)
    
    def run(self):
        """运行游戏主循环"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(GameConfig.FPS)
        
        pygame.quit()
        sys.exit()