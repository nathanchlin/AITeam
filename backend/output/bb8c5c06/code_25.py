def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("贪吃蛇游戏")
    clock = pygame.time.Clock()
    
    # 初始化游戏状态
    snake, direction, food, score = reset_game()
    game_over = False
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if not game_over:
                # 处理方向键输入
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP and direction != [0, 1]:
                        direction = [0, -1]
                    elif event.key == pygame.K_DOWN and direction != [0, -1]:
                        direction = [0, 1]
                    elif event.key == pygame.K_LEFT and direction != [1, 0]:
                        direction = [-1, 0]
                    elif event.key == pygame.K_RIGHT and direction != [-1, 0]:
                        direction = [1, 0]
            else:
                # 游戏结束后按空格键重新开始
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        snake, direction, food, score = reset_game()
                        game_over = False
        
        if not game_over:
            # 移动蛇
            new_head = [snake[0][0] + direction[0], snake[0][1] + direction[1]]
            snake.insert(0, new_head)
            
            # 检查是否吃到食物
            if snake[0] == food:
                score += 1
                food = generate_food(snake)
            else:
                snake.pop()
            
            # 检查碰撞
            if check_collision(snake):
                game_over = True
        
        # 绘制游戏
        draw_game(screen, snake, food, score)
        
        # 如果游戏结束，绘制游戏结束画面
        if game_over:
            draw_game_over(screen, score)
        
        # 控制游戏速度
        clock.tick(SPEED)
    
    pygame.quit()

if __name__ == "__main__":
    # 游戏常量
    GRID_WIDTH = 20
    GRID_HEIGHT = 15
    CELL_SIZE = 30
    SCREEN_WIDTH = GRID_WIDTH * CELL_SIZE
    SCREEN_HEIGHT = GRID_HEIGHT * CELL_SIZE
    SPEED = 10
    
    # 运行游戏
    main()