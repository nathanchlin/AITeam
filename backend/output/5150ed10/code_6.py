class Game:
    def __init__(self, screen_width=800, screen_height=600):
        pygame.init()
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("男人就要撑过100秒")
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_time = 0
        self.font = pygame.font.SysFont('Arial', 24)
        
        # 玩家设置
        self.player_rect = pygame.Rect(50, screen_height // 2, 40, 40)
        self.player_speed = 5
        
        # 障碍物生成器
        self.obstacle_generator = ObstacleGenerator(screen_width, screen_height)
        
        # 碰撞检测器
        self.collision_detector = CollisionDetector()
        
        # 游戏状态
        self.game_over = False
        self.score = 0
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and self.game_over:
                    self.__init__()
        
        if not self.game_over:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP] and self.player_rect.top > 0:
                self.player_rect.y -= self.player_speed
            if keys[pygame.K_DOWN] and self.player_rect.bottom < self.screen.get_height():
                self.player_rect.y += self.player_speed
            if keys[pygame.K_LEFT] and self.player_rect.left > 0:
                self.player_rect.x -= self.player_speed
            if keys[pygame.K_RIGHT] and self.player_rect.right < self.screen.get_width():
                self.player_rect.x += self.player_speed
    
    def update(self):
        if not self.game_over:
            self.game_time += self.clock.get_time()
            self.score = self.game_time // 100  # 每100毫秒得1分
            
            # 更新障碍物
            self.obstacle_generator.update_obstacles(self.game_time)
            
            # 碰撞检测
            collision, obstacle_type = self.collision_detector.check_collision(
                self.player_rect, self.obstacle_generator.obstacles
            )
            
            if collision:
                self.game_over = True
    
    def draw(self):
        self.screen.fill((0, 0, 0))  # 黑色背景
        
        if not self.game_over:
            # 绘制玩家
            pygame.draw.rect(self.screen, (0, 255, 0), self.player_rect)
            
            # 绘制障碍物
            self.obstacle_generator.draw_obstacles(self.screen)
            
            # 显示游戏时间和分数
            time_text = self.font.render(f"时间: {self.score}秒", True, (255, 255, 255))
            self.screen.blit(time_text, (10, 10))
            
            # 显示当前难度
            difficulty_text = self.font.render(
                f"难度: {self.obstacle_generator.difficulty.name}", True, (255, 255, 255)
            )
            self.screen.blit(difficulty_text, (10, 40))
        else:
            # 游戏结束画面
            game_over_text = self.font.render("游戏结束! 按空格键重新开始", True, (255, 255, 255))
            text_rect = game_over_text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
            self.screen.blit(game_over_text, text_rect)
            
            score_text = self.font.render(f"最终得分: {self.score}秒", True, (255, 255, 255))
            score_rect = score_text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 + 40))
            self.screen.blit(score_text, score_rect)
        
        pygame.display.flip()
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)  # 60 FPS
        
        pygame.quit()

# 启动游戏
if __name__ == "__main__":
    game = Game()
    game.run()