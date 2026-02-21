def create_bricks():
    """创建砖块"""
    bricks = []
    rows = 5
    cols = 10
    brick_width = 75
    brick_height = 20
    padding = 10
    offset_x = 35
    offset_y = 60
    
    for row in range(rows):
        for col in range(cols):
            x = col * (brick_width + padding) + offset_x
            y = row * (brick_height + padding) + offset_y
            bricks.append(Brick(x, y, brick_width, brick_height))
    
    return bricks

def update_paddle(paddle):
    """更新挡板位置"""
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        paddle.move_left()
    if keys[pygame.K_RIGHT]:
        paddle.move_right()

def update_ball(ball):
    """更新球的位置"""
    ball.move()
    
    # 边界碰撞检测
    if ball.x <= 0 or ball.x >= SCREEN_WIDTH - ball.radius:
        ball.bounce_x()
    if ball.y <= 0:
        ball.bounce_y()

def check_ball_paddle_collision(ball, paddle):
    """检测球和挡板的碰撞"""
    if (ball.y + ball.radius >= paddle.y and 
        ball.y - ball.radius <= paddle.y + paddle.height and
        ball.x >= paddle.x and 
        ball.x <= paddle.x + paddle.width):
        return True
    return False

def check_ball_bricks_collision(ball, bricks):
    """检测球和砖块的碰撞"""
    for brick in bricks:
        if (ball.x + ball.radius >= brick.x and 
            ball.x - ball.radius <= brick.x + brick.width and
            ball.y + ball.radius >= brick.y and 
            ball.y - ball.radius <= brick.y + brick.height):
            return brick
    return None

def reset_ball(ball):
    """重置球的位置"""
    ball.reset()

def draw_game(game_state, paddle, ball, bricks):
    """绘制游戏画面"""
    screen.fill((0, 0, 0))
    
    # 绘制游戏元素
    paddle.draw(screen)
    ball.draw(screen)
    for brick in bricks:
        brick.draw(screen)
    
    # 绘制UI
    draw_ui(game_state)
    
    # 根据游戏状态绘制不同的界面
    if game_state.current_state == GameState.MENU:
        draw_menu()
    elif game_state.current_state == GameState.PAUSED:
        draw_pause_screen()
    elif game_state.current_state == GameState.GAME_OVER:
        draw_game_over(game_state)
    elif game_state.current_state == GameState.WIN:
        draw_win_screen(game_state)
    
    pygame.display.flip()

def draw_ui(game_state):
    """绘制游戏UI"""
    font = pygame.font.SysFont('Arial', 20)
    
    # 绘制分数
    score_text = font.render(f"Score: {game_state.score}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))
    
    # 绘制生命值
    lives_text = font.render(f"Lives: {game_state.lives}", True, (255, 255, 255))
    screen.blit(lives_text, (SCREEN_WIDTH - 100, 10))
    
    # 绘制最高分
    high_score_text = font.render(f"High Score: {game_state.high_score}", True, (255, 255, 255))
    screen.blit(high_score_text, (SCREEN_WIDTH // 2 - 70, 10))
    
    # 绘制关卡
    level_text = font.render(f"Level: {game_state.level}", True, (255, 255, 255))
    screen.blit(level_text, (SCREEN_WIDTH // 2 - 40, 40))

def draw_menu():
    """绘制菜单界面"""
    font = pygame.font.SysFont('Arial', 50)
    title_text = font.render("BREAKOUT", True, (255, 255, 255))
    screen.blit(title_text, (SCREEN_WIDTH // 2 - 100, 200))
    
    font = pygame.font.SysFont('Arial', 30)
    start_text = font.render("Press SPACE to Start", True, (255, 255, 255))
    screen.blit(start_text, (SCREEN_WIDTH // 2 - 120, 300))
    
    controls_text = font.render("Use LEFT/RIGHT arrows to move", True, (255, 255, 255))
    screen.blit(controls_text, (SCREEN_WIDTH // 2 - 180, 350))

def draw_pause_screen():
    """绘制暂停界面"""
    font = pygame.font.SysFont('Arial', 50)
    pause_text = font.render("PAUSED", True, (255, 255, 255))
    screen.blit(pause_text, (SCREEN_WIDTH // 2 - 80, 200))
    
    font = pygame.font.SysFont('Arial', 30)
    resume_text = font.render("Press ESC to Resume", True, (255, 255, 255))
    screen.blit(resume_text, (SCREEN_WIDTH // 2 - 130, 300))

def draw_game_over(game_state):
    """绘制游戏结束界面"""
    font = pygame.font.SysFont('Arial', 50)
    game_over_text = font.render("GAME OVER", True, (255, 0, 0))
    screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 120, 200))
    
    font = pygame.font.SysFont('Arial', 30)
    score_text = font.render(f"Final Score: {game_state.score}", True, (255, 255, 255))
    screen.blit(score_text, (SCREEN_WIDTH // 2 - 100, 300))
    
    restart_text = font.render("Press SPACE to Return to Menu", True, (255, 255, 255))
    screen.blit(restart_text, (SCREEN_WIDTH // 2 - 180, 350))

def draw_win_screen(game_state):
    """绘制胜利界面"""
    font = pygame.font.SysFont('Arial', 50)
    win_text = font.render("YOU WIN!", True, (0, 255, 0))
    screen.blit(win_text, (SCREEN_WIDTH // 2 - 80, 200))
    
    font = pygame.font.SysFont('Arial', 30)
    score_text = font.render(f"Final Score: {game_state.score}", True, (255, 255, 255))
    screen.blit(score_text, (SCREEN_WIDTH // 2 - 100, 300))
    
    restart_text = font.render("Press SPACE to Return to Menu", True, (255, 255, 255))
    screen.blit(restart_text, (SCREEN_WIDTH // 2 - 180, 350))