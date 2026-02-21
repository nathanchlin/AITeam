def game_loop():
    # 初始化
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Enhanced Tetris")
    clock = pygame.time.Clock()
    
    # 游戏状态
    board = create_board()
    current_piece = get_new_piece()
    next_piece = get_new_piece()
    score = 0
    level = 1
    lines = 0
    game_over = False
    fall_time = 0
    fall_speed = 500  # 毫秒
    
    # 游戏主循环
    running = True
    while running:
        screen.fill((0, 0, 0))
        
        # 绘制游戏背景
        draw_game_background(screen, GAME_WIDTH, GAME_HEIGHT)
        
        # 绘制游戏板
        draw_board(screen, board, 10, 10)
        
        # 绘制当前方块
        if current_piece:
            draw_tetromino(screen, 10, 10, current_piece.shape, current_piece.x, current_piece.y)
            
            # 绘制阴影
            draw_shadow(screen, board, current_piece, 10, 10)
        
        # 绘制下一个方块
        draw_next_piece(screen, next_piece, GAME_WIDTH + 20, 20)
        
        # 绘制分数信息
        draw_score_info(screen, score, level, lines, GAME_WIDTH + 20, 160)
        
        # 游戏结束画面
        if game_over:
            draw_game_over(screen, score, SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # 处理事件
        for event in pygame.event.get():
            # ... 原有的事件处理代码 ...
        
        # 更新游戏状态
        if not game_over:
            # ... 原有的游戏逻辑 ...
        
        # 更新显示
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()