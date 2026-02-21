def game_loop():
    """游戏主循环"""
    game_state = GameState()
    paddle = Paddle()
    ball = Ball()
    bricks = create_bricks()  # 创建砖块
    
    clock = pygame.time.Clock()
    running = True
    
    while running:
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if game_state.current_state == GameState.PLAYING:
                        game_state.toggle_pause()
                    elif game_state.current_state == GameState.PAUSED:
                        game_state.toggle_pause()
                        
                if event.key == pygame.K_SPACE:
                    if game_state.current_state == GameState.MENU:
                        game_state.start_game()
                    elif game_state.current_state == GameState.GAME_OVER or game_state.current_state == GameState.WIN:
                        game_state.back_to_menu()
                        game_state.reset_game()
        
        # 根据当前状态更新游戏
        if game_state.current_state == GameState.PLAYING:
            # 更新游戏逻辑
            update_paddle(paddle)
            update_ball(ball)
            
            # 检测碰撞
            if check_ball_paddle_collision(ball, paddle):
                ball.bounce_off_paddle()
                
            brick_hit = check_ball_bricks_collision(ball, bricks)
            if brick_hit:
                game_state.add_score(10)  # 每个砖块10分
                bricks.remove(brick_hit)
                
            # 检查游戏条件
            if ball.y > SCREEN_HEIGHT:
                game_state.lose_life()
                reset_ball(ball)
                
            game_state.check_win_condition(bricks)
            
        # 绘制游戏
        draw_game(game_state, paddle, ball, bricks)
        
        clock.tick(60)  # 60 FPS
    
    pygame.quit()