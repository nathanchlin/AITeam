class GameController:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.player = PlayerAircraft(screen_width // 2, screen_height - 100, screen_width, screen_height)
        self.bullets = []
        self.enemies = []  # 敌机列表，将在敌机系统中实现
        self.score = 0
        self.game_over = False
        self.font = pygame.font.SysFont('Arial', 24)
        
    def update(self, keys):
        """更新游戏状态"""
        if self.game_over:
            return
            
        # 更新玩家
        new_bullets = self.player.update(keys)
        if new_bullets:
            self.bullets.extend(new_bullets)
            
        # 更新子弹
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.is_off_screen(self.screen_width, self.screen_height):
                self.bullets.remove(bullet)
                
        # 碰撞检测（子弹与敌机）
        self.check_collisions()
        
    def check_collisions(self):
        """检测碰撞"""
        # 这里可以添加子弹与敌机的碰撞检测
        # 简化示例：检查子弹是否击中了屏幕边界
        pass
        
    def draw(self, screen):
        """绘制游戏画面"""
        # 绘制玩家
        self.player.draw(screen)
        
        # 绘制子弹
        for bullet in self.bullets:
            bullet.draw(screen)
            
        # 绘制分数
        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
        
        # 绘制游戏结束画面
        if self.game_over:
            game_over_text = self.font.render("GAME OVER", True, (255, 0, 0))
            restart_text = self.font.render("Press R to Restart", True, (255, 255, 255))
            
            text_rect = game_over_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            restart_rect = restart_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 40))
            
            screen.blit(game_over_text, text_rect)
            screen.blit(restart_text, restart_rect)
            
    def handle_events(self, event):
        """处理事件"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                self.player.change_weapon(WeaponType.BASIC)
            elif event.key == pygame.K_2:
                self.player.change_weapon(WeaponType.SPREAD)
            elif event.key == pygame.K_3:
                self.player.change_weapon(WeaponType.LASER)
            elif event.key == pygame.K_r and self.game_over:
                self.restart_game()
                
    def restart_game(self):
        """重新开始游戏"""
        self.player = PlayerAircraft(self.screen_width // 2, self.screen_height - 100, 
                                    self.screen_width, self.screen_height)
        self.bullets = []
        self.enemies = []
        self.score = 0
        self.game_over = False