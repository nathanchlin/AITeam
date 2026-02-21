def game_loop():
    # 初始化
    clock = pygame.time.Clock()
    collision_detector = CollisionDetector()
    game_state = GameState()
    bird = Bird()
    pipes = []
    
    # 主循环
    running = True
    while running:
        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if game_state.state == "MENU":
                        game_state.transition("PLAYING")
                        bird.reset()
                        pipes.clear()
                    elif game_state.state == "PLAYING":
                        bird.jump()
                    elif game_state.state == "GAME_OVER":
                        game_state.transition("MENU")
        
        # 更新游戏状态
        if game_state.state == "PLAYING":
            # 更新小鸟位置
            bird.update()
            
            # 生成新管道
            if len(pipes) == 0 or pipes[-1][0] < SCREEN_WIDTH - 200:
                pipes.append(generate_pipe())
            
            # 更新管道位置
            pipes = [(x - 5, top_height, bottom_y, gap_y, gap_height, scored) 
                    for x, top_height, bottom_y, gap_y, gap_height, scored in pipes]
            
            # 移除屏幕外的管道
            pipes = [pipe for pipe in pipes if pipe[0] + PIPE_WIDTH > 0]
            
            # 碰撞检测
            if collision_detector.check_collision(
                (bird.x, bird.y, bird.radius), 
                pipes, 
                GROUND_HEIGHT, 
                SCREEN_WIDTH
            ):
                game_state.transition("GAME_OVER")
            
            # 计分检测
            scored_pipes = collision_detector.check_score(
                (bird.x, bird.y, bird.radius), 
                pipes
            )
            for i in scored_pipes:
                pipes[i] = (pipes[i][0], pipes[i][1], pipes[i][2], 
                           pipes[i][3], pipes[i][4], True)
                game_state.score += 1
        
        # 渲染
        render(game_state, bird, pipes)
        
        # 控制帧率
        clock.tick(60)
    
    pygame.quit()