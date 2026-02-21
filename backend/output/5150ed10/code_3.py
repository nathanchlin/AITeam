class Game:
    def __init__(self):
        """初始化游戏"""
        pygame.init()
        self.screen_width = 800
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("男人就要撑过100秒")
        self.clock = pygame.time.Clock()
        
        # 游戏对象
        self.player = PlayerPlane(self.screen_width // 2 - 20, self.screen_height - 70, 
                                 self.screen_width, self.screen_height)
        self.bullets = []
        
        # 游戏状态
        self.running = True
        self.game_time = 0
        self.font = pygame.font.SysFont(None, 36)
        
    def handle_events(self):
        """处理游戏事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # 射击
                    bullet = self.player.shoot()
                    if bullet:
                        self.bullets.append(bullet)
                        
    def update(self):
        """更新游戏状态"""
        keys = pygame.key.get_pressed()
        self.player.update(keys)
        
        # 更新子弹
        for bullet in self.bullets[:]:
            bullet.update()
            if not bullet.active:
                self.bullets.remove(bullet)
                
        # 更新游戏时间
        self.game_time += 1
        
    def draw(self):
        """绘制游戏画面"""
        self.screen.fill((0, 0, 0))  # 黑色背景
        
        # 绘制玩家
        self.player.draw(self.screen)
        
        # 绘制子弹
        for bullet in self.bullets:
            bullet.draw(self.screen)
            
        # 绘制游戏时间
        time_text = self.font.render(f"时间: {self.game_time // 60}秒", True, (255, 255, 255))
        self.screen.blit(time_text, (10, 10))
        
        # 如果玩家死亡，显示游戏结束
        if not self.player.is_alive:
            game_over_text = self.font.render("游戏结束! 按R重新开始", True, (255, 0, 0))
            text_rect = game_over_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.screen.blit(game_over_text, text_rect)
            
        pygame.display.flip()
        
    def run(self):
        """运行游戏主循环"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)  # 60 FPS
            
        pygame.quit()