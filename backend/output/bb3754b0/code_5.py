class FlappyBirdGame:
    def __init__(self, width=800, height=600):
        """初始化游戏"""
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Flappy Bird")
        
        # 游戏参数
        self.width = width
        self.height = height
        self.clock = pygame.time.Clock()
        self.running = True
        
        # 初始化鸟
        self.bird = Bird(100, height // 2)
        
        # 初始化管道管理器
        self.pipe_manager = PipeManager(width, height)
        
        # 游戏状态
        self.game_over = False
        self.font = pygame.font.SysFont(None, 36)
    
    def run(self):
        """运行游戏主循环"""
        while self.running:
            # 处理事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if self.game_over:
                            self.reset_game()
                        else:
                            self.bird.jump()
            
            if not self.game_over:
                # 更新游戏状态
                self.update()
            
            # 绘制游戏
            self.draw()
            
            # 控制帧率
            self.clock.tick(60)
        
        pygame.quit()
    
    def update(self):
        """更新游戏状态"""
        # 更新鸟
        self.bird.update()
        
        # 更新管道
        current_time = pygame.time.get_ticks()
        self.pipe_manager.update(current_time)
        
        # 检查碰撞
        bird_rect = pygame.Rect(self.bird.x, self.bird.y, 
                               self.bird.width, self.bird.height)
        
        if self.pipe_manager.check_collisions(bird_rect) or \
           self.bird.y < 0 or self.bird.y + self.bird.height > self.height:
            self.game_over = True
        
        # 检查通过的管道
        self.pipe_manager.check_passed_pipes(bird_rect)
    
    def draw(self):
        """绘制游戏画面"""
        # 清屏
        self.screen.fill((135, 206, 235))  # 天空蓝
        
        # 绘制管道
        self.pipe_manager.draw(self.screen)
        
        # 绘制鸟
        self.bird.draw(self.screen)
        
        # 绘制分数
        score_text = self.font.render(f"Score: {self.pipe_manager.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))
        
        # 游戏结束提示
        if self.game_over:
            game_over_text = self.font.render("Game Over! Press Space to Restart", True, (255, 255, 255))
            text_rect = game_over_text.get_rect(center=(self.width//2, self.height//2))
            self.screen.blit(game_over_text, text_rect)
        
        # 更新显示
        pygame.display.flip()
    
    def reset_game(self):
        """重置游戏"""
        self.game_over = False
        self.bird.reset()
        self.pipe_manager.reset()

# 鸟类 (简单实现)
class Bird:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 34
        self.height = 24
        self.velocity = 0
        self.gravity = 0.5
        self.jump_strength = -8
        self.color = (255, 255, 0)  # 黄色
    
    def jump(self):
        """鸟跳跃"""
        self.velocity = self.jump_strength
    
    def update(self):
        """更新鸟的位置"""
        self.velocity += self.gravity
        self.y += self.velocity
    
    def draw(self, screen):
        """绘制鸟"""
        pygame.draw.ellipse(screen, self.color, 
                           (self.x, self.y, self.width, self.height))
    
    def reset(self):
        """重置鸟的位置"""
        self.y = 300
        self.velocity = 0