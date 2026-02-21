class Ball:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = BALL_RADIUS
        self.speed_x = 5
        self.speed_y = -5
        self.color = WHITE
        self.trail = []  # 用于实现拖尾效果
        
    def move(self):
        # 更新位置
        self.x += self.speed_x
        self.y += self.speed_y
        
        # 边界碰撞检测
        if self.x <= self.radius or self.x >= SCREEN_WIDTH - self.radius:
            self.speed_x = -self.speed_x
        if self.y <= self.radius:
            self.speed_y = -self.speed_y
            
        # 添加当前位置到轨迹
        self.trail.append((self.x, self.y))
        if len(self.trail) > 10:  # 限制轨迹长度
            self.trail.pop(0)
    
    def draw(self, screen):
        # 绘制轨迹
        for i, pos in enumerate(self.trail):
            alpha = int(255 * (i / len(self.trail)))
            pygame.draw.circle(screen, (*self.color, alpha), (int(pos[0]), int(pos[1])), 
                              int(self.radius * (i / len(self.trail))))
        
        # 绘制球体
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        
        # 添加高光效果
        highlight_x = int(self.x - self.radius * 0.3)
        highlight_y = int(self.y - self.radius * 0.3)
        highlight_radius = int(self.radius * 0.3)
        pygame.draw.circle(screen, WHITE, (highlight_x, highlight_y), highlight_radius)
    
    def reset(self, x, y):
        self.x = x
        self.y = y
        self.speed_x = 5 * random.choice([-1, 1])
        self.speed_y = -5
        self.trail = []

class Paddle:
    def __init__(self, x, y):
        self.width = PADDLE_WIDTH
        self.height = PADDLE_HEIGHT
        self.x = x
        self.y = y
        self.color = CYAN
        self.speed = 8
        self.moving_left = False
        self.moving_right = False
        
    def move(self):
        if self.moving_left and self.x > 0:
            self.x -= self.speed
        if self.moving_right and self.x < SCREEN_WIDTH - self.width:
            self.x += self.speed
            
    def draw(self, screen):
        # 绘制主体
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        
        # 添加高光效果
        pygame.draw.rect(screen, WHITE, (self.x, self.y, self.width, 3))
        
        # 添加边框
        pygame.draw.rect(screen, BLACK, (self.x, self.y, self.width, self.height), 2)

class Brick:
    def __init__(self, x, y, color, hits=1):
        self.width = BRICK_WIDTH
        self.height = BRICK_HEIGHT
        self.x = x
        self.y = y
        self.color = color
        self.hits = hits
        self.max_hits = hits
        self.visible = True
        self.destroy_animation = 0
        
    def hit(self):
        self.hits -= 1
        if self.hits <= 0:
            self.visible = False
            return True
        return False
    
    def draw(self, screen):
        if not self.visible:
            # 破坏动画
            if self.destroy_animation < 10:
                self.destroy_animation += 1
                for i in range(5):
                    x = self.x + random.randint(0, self.width)
                    y = self.y + random.randint(0, self.height)
                    pygame.draw.circle(screen, self.color, (x, y), random.randint(1, 3))
                return
        
        # 根据剩余生命值调整颜色亮度
        brightness = self.hits / self.max_hits
        color = tuple(int(c * brightness) for c in self.color)
        
        # 绘制砖块主体
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))
        
        # 添加高光效果
        pygame.draw.rect(screen, WHITE, (self.x, self.y, self.width, 3))
        
        # 添加边框
        pygame.draw.rect(screen, BLACK, (self.x, self.y, self.width, self.height), 1)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("打砖块游戏")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 24)
        
        self.reset_game()
        
    def reset_game(self):
        # 初始化游戏对象
        self.ball = Ball(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
        self.paddle = Paddle((SCREEN_WIDTH - PADDLE_WIDTH) // 2, SCREEN_HEIGHT - 30)
        self.bricks = self.create_bricks()
        
        # 游戏状态
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.game_won = False
        self.paused = False
        
    def create_bricks(self):
        bricks = []
        colors = [RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE]
        
        # 创建多行砖块
        for row in range(6):
            for col in range(10):
                x = col * (BRICK_WIDTH + BRICK_PADDING) + BRICK_OFFSET_LEFT
                y = row * (BRICK_HEIGHT + BRICK_PADDING) + BRICK_OFFSET_TOP
                color = colors[row % len(colors)]
                hits = 1 if row < 2 else (2 if row < 4 else 3)  # 上面的砖块更难打碎
                bricks.append(Brick(x, y, color, hits))
                
        return bricks
    
    def check_collisions(self):
        # 球与挡板碰撞
        if (self.ball.y + self.ball.radius >= self.paddle.y and
            self.ball.y - self.ball.radius <= self.paddle.y + self.paddle.height and
            self.ball.x >= self.paddle.x and
            self.ball.x <= self.paddle.x + self.paddle.width):
            
            # 计算碰撞点相对于挡板中心的位置
            hit_pos = (self.ball.x - self.paddle.x) / self.paddle.width
            # 根据碰撞点调整反弹角度
            self.ball.speed_x = 8 * (hit_pos - 0.5)
            self.ball.speed_y = -abs(self.ball.speed_y)
            
        # 球与砖块碰撞
        for brick in self.bricks:
            if brick.visible:
                if (self.ball.x + self.ball.radius >= brick.x and
                    self.ball.x - self.ball.radius <= brick.x + brick.width and
                    self.ball.y + self.ball.radius >= brick.y and
                    self.ball.y - self.ball.radius <= brick.y + brick.height):
                    
                    # 确定碰撞方向
                    ball_left = self.ball.x - self.ball.radius
                    ball_right = self.ball.x + self.ball.radius
                    ball_top = self.ball.y - self.ball.radius
                    ball_bottom = self.ball.y + self.ball.radius
                    
                    brick_left = brick.x
                    brick_right = brick.x + brick.width
                    brick_top = brick.y
                    brick_bottom = brick.y + brick.height
                    
                    # 计算重叠量
                    overlap_left = ball_right - brick_left
                    overlap_right = brick_right - ball_left
                    overlap_top = ball_bottom - brick_top
                    overlap_bottom = brick_bottom - ball_top
                    
                    # 找出最小重叠方向
                    min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)
                    
                    if min_overlap == overlap_left or min_overlap == overlap_right:
                        self.ball.speed_x = -self.ball.speed_x
                    else:
                        self.ball.speed_y = -self.ball.speed_y
                    
                    if brick.hit():
                        self.score += 10 * brick.max_hits
                    
                    break
    
    def update(self):
        if not self.game_over and not self.game_won and not self.paused:
            self.ball.move()
            self.paddle.move()
            self.check_collisions()
            
            # 检查球是否掉落
            if self.ball.y > SCREEN_HEIGHT:
                self.lives -= 1
                if self.lives <= 0:
                    self.game_over = True
                else:
                    self.ball.reset(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
            
            # 检查是否获胜
            if all(not brick.visible for brick in self.bricks):
                self.game_won = True
    
    def draw(self):
        # 绘制背景
        self.screen.fill(BLACK)
        
        # 绘制游戏对象
        self.ball.draw(self.screen)
        self.paddle.draw(self.screen)
        
        for brick in self.bricks:
            brick.draw(self.screen)
        
        # 绘制UI
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        lives_text = self.font.render(f"Lives: {self.lives}", True, WHITE)
        self.screen.blit(lives_text, (SCREEN_WIDTH - 120, 10))
        
        if self.game_over:
            game_over_text = self.font.render("GAME OVER", True, RED)
            restart_text = self.small_font.render("Press SPACE to restart", True, WHITE)
            self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2))
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 40))
        
        if self.game_won:
            win_text = self.font.render("YOU WIN!", True, GREEN)
            restart_text = self.small_font.render("Press SPACE to restart", True, WHITE)
            self.screen.blit(win_text, (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2))
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 40))
        
        if self.paused and not self.game_over and not self.game_won:
            pause_text = self.font.render("PAUSED", True, YELLOW)
            self.screen.blit(pause_text, (SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT // 2))
        
        # 绘制操作提示
        if not self.game_over and not self.game_won:
            help_text = self.small_font.render("Use LEFT/RIGHT arrows to move, P to pause", True, WHITE)
            self.screen.blit(help_text, (SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT - 20))
        
        pygame.display.flip()
    
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.paddle.moving_left = True
                    elif event.key == pygame.K_RIGHT:
                        self.paddle.moving_right = True
                    elif event.key == pygame.K_SPACE:
                        if self.game_over or self.game_won:
                            self.reset_game()
                        elif self.paused:
                            self.paused = False
                        else:
                            self.paused = True
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.paddle.moving_left = False
                    elif event.key == pygame.K_RIGHT:
                        self.paddle.moving_right = False
            
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

# 运行游戏
if __name__ == "__main__":
    game = Game()
    game.run()