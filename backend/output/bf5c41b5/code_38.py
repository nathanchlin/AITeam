def main_game_loop():
    # 初始化游戏
    game = BrickBreakerGame()
    renderer = GameRenderer(game)
    state_manager = GameStateManager()
    
    # 游戏主循环
    running = True
    clock = pygame.time.Clock()
    
    while running:
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if state_manager.current_state == 'playing':
                        state_manager.pause_game()
                    elif state_manager.current_state == 'paused':
                        state_manager.resume_game()
                    elif state_manager.current_state == 'game_over':
                        state_manager.back_to_menu()
                elif event.key == pygame.K_SPACE and state_manager.current_state == 'menu':
                    state_manager.start_game()
                    game = BrickBreakerGame()  # 重置游戏
        
        # 更新游戏状态
        if state_manager.current_state == 'playing':
            # 更新球的位置
            # 检查碰撞
            game.handle_ball_collision(ball_pos, ball_dir)
            
            # 检查球是否掉落
            if game.check_ball_fall():
                if game.get_game_status()['game_over']:
                    state_manager.end_game(game.score_system.score)
                else:
                    # 重置球的位置
                    pass
            
            # 检查是否所有砖块都被消除
            if game.get_game_status()['all_bricks_cleared']:
                state_manager.end_game(game.score_system.score)
        
        # 渲染游戏
        renderer.render_game()
        
        # 控制帧率
        clock.tick(60)
    
    pygame.quit()