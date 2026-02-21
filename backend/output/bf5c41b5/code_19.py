def main():
    # 初始化Pygame
    pygame.init()
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("打砖块游戏")
    clock = pygame.time.Clock()
    
    # 创建游戏对象
    ball = BallPhysics(width // 2, height - 100, 10, 200, -200)
    paddle = Paddle(width // 2 - 50, height - 30, 100, 10, 300)
    
    # 创建砖块
    bricks = []
    brick_rows = 5
    brick_cols = 10
    brick_width = 70
    brick_height = 20
    brick_padding = 5
    brick_offset_x = (width - (brick_cols * (brick_width + brick_padding))) // 2
    brick_offset_y = 60
    
    for row in range(brick_rows):
        for col in range(brick_cols):
            x = brick_offset_x + col * (brick_width + brick_padding)
            y = brick_offset_y + row * (brick_height + brick_padding)
            color = (
                255 * (row / brick_rows),
                100,
                255 * (1 - row / brick_rows)
            )
            hits = brick_rows - row  # 上面的砖块需要更多击中次数
            bricks.append(Brick(x, y, brick_width, brick_height, color, hits))
    
    # 游戏状态
    running = True
    game_over = False
    game_won = False
    score = 0
    
    # 主游戏循环
    while running:
        dt = clock.tick(60) / 1000.0  # 转换为秒
        
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    paddle.moving_left = True
                elif event.key == pygame.K_RIGHT:
                    paddle.moving_right = True
                elif event.key == pygame.K_SPACE and game_over:
                    # 重置游戏
                    ball = BallPhysics(width // 2, height - 100, 10, 200, -200)
                    paddle = Paddle(width // 2 - 50, height - 30, 100, 10, 300)
                    bricks = []
                    for row in range(brick_rows):
                        for col in range(brick_cols):
                            x = brick_offset_x + col * (brick_width + brick_padding)
                            y = brick_offset_y + row * (brick_height + brick_padding)
                            color = (
                                255 * (row / brick_rows),
                                100,
                                255 * (1 - row / brick_rows)
                            )
                            hits = brick_rows - row
                            bricks.append(Brick(x, y, brick_width, brick_height, color, hits))
                    game_over = False
                    game_won = False
                    score = 0
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    paddle.moving_left = False
                elif event.key == pygame.K_RIGHT:
                    paddle.moving_right = False
        
        if not game_over:
            # 更新游戏对象
            ball.update(dt)
            paddle.update(dt, width)
            
            # 边界碰撞检测
            ball.check_boundary_collision(width, height)
            
            # 挡板碰撞检测
            ball.check_paddle_collision(paddle)
            
            # 砖块碰撞检测
            for brick in bricks[:]:
                if ball.check_brick_collision(brick):
                    if brick.hit():
                        bricks.remove(brick)
                        score += 10 * brick.max_hits
            
            # 检查游戏结束条件
            if ball.y + ball.radius >= height:
                game_over = True
            elif len(bricks) == 0:
                game_won = True
                game_over = True
        
        # 绘制
        screen.fill((0, 0, 0))
        
        # 绘制游戏对象
        ball.draw(screen)
        paddle.draw(screen)
        for brick in bricks:
            brick.draw(screen)
        
        # 显示分数
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
        
        # 显示游戏结束信息
        if game_over:
            if game_won:
                text = font.render("You Win! Press Space to Play Again", True, (0, 255, 0))
            else:
                text = font.render("Game Over! Press Space to Play Again", True, (255, 0, 0))
            text_rect = text.get_rect(center=(width // 2, height // 2))
            screen.blit(text, text_rect)
        
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    main()