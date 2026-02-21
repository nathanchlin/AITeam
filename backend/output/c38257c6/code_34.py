def main():
    pygame.init()
    screen_width = 800
    screen_height = 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("打砖块游戏")
    clock = pygame.time.Clock()
    
    # 初始化游戏组件
    paddle = Paddle(screen_width // 2 - 50, screen_height - 30, 100, 15, (0, 255, 0))
    ball = Ball(screen_width // 2, screen_height - 50, 10, 5, -5, (255, 255, 255))
    
    # 创建砖块布局
    brick_layout = BrickLayout(6, 10, 75, 25, 5)
    brick_layout.create_layout()
    
    brick_manager = BrickManager()
    
    running = True
    game_over = False
    game_won = False
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    paddle.move_left()
                elif event.key == pygame.K_RIGHT:
                    paddle.move_right()
                elif event.key == pygame.K_SPACE and (game_over or game_won):
                    # 重新开始游戏
                    ball = Ball(screen_width // 2, screen_height - 50, 10, 5, -5, (255, 255, 255))
                    brick_layout.create_layout()
                    brick_manager = BrickManager()
                    game_over = False
                    game_won = False
        
        if not game_over and not game_won:
            # 更新挡板位置
            paddle.update(screen_width)
            
            # 更新球的位置
            ball.update(screen_width, screen_height)
            
            # 检测球与挡板的碰撞
            if ball.check_paddle_collision(paddle):
                ball.dy = -ball.dy
            
            # 检测球与砖块的碰撞
            brick_manager.handle_brick_collision(ball, brick_layout.bricks)
            
            # 检查是否所有砖块都被消除
            if brick_layout.is_cleared():
                game_won = True
            
            # 检查球是否掉落底部
            if ball.y > screen_height:
                game_over = True
        
        # 绘制游戏元素
        screen.fill((0, 0, 0))
        paddle.draw(screen)
        ball.draw(screen)
        brick_layout.draw(screen)
        
        # 显示得分
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Score: {brick_manager.get_score()}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
        
        # 显示游戏结束或胜利信息
        if game_over:
            game_over_text = font.render("Game Over! Press Space to Restart", True, (255, 0, 0))
            screen.blit(game_over_text, (screen_width // 2 - 150, screen_height // 2))
        elif game_won:
            win_text = font.render("You Win! Press Space to Restart", True, (0, 255, 0))
            screen.blit(win_text, (screen_width // 2 - 150, screen_height // 2))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

# 挡板和球的类（假设已实现）
class Paddle:
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.speed = 8
    
    def move_left(self):
        self.x -= self.speed
    
    def move_right(self):
        self.x += self.speed
    
    def update(self, screen_width):
        # 确保挡板不会移出屏幕
        if self.x < 0:
            self.x = 0
        elif self.x + self.width > screen_width:
            self.x = screen_width - self.width
    
    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))

class Ball:
    def __init__(self, x, y, radius, dx, dy, color):
        self.x = x
        self.y = y
        self.radius = radius
        self.dx = dx
        self.dy = dy
        self.color = color
    
    def update(self, screen_width, screen_height):
        self.x += self.dx
        self.y += self.dy
        
        # 边界碰撞检测
        if self.x - self.radius < 0 or self.x + self.radius > screen_width:
            self.dx = -self.dx
        if self.y - self.radius < 0:
            self.dy = -self.dy
    
    def check_paddle_collision(self, paddle):
        ball_rect = pygame.Rect(self.x - self.radius, self.y - self.radius, 
                               self.radius * 2, self.radius * 2)
        paddle_rect = pygame.Rect(paddle.x, paddle.y, paddle.width, paddle.height)
        
        if ball_rect.colliderect(paddle_rect):
            # 计算碰撞点相对于挡板中心的位置
            hit_pos = (self.x - (paddle.x + paddle.width / 2)) / (paddle.width / 2)
            # 根据碰撞位置调整球的水平速度
            self.dx = hit_pos * 5
            self.dy = -self.dy
            return True
        return False
    
    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

if __name__ == "__main__":
    main()