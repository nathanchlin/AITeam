# 初始化
visual_effects = VisualEffects(SCREEN_WIDTH, SCREEN_HEIGHT)

# 主游戏循环
clock = pygame.time.Clock()
running = True

while running:
    dt = clock.tick(60) / 1000.0  # 转换为秒
    
    # 处理事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
            if not game_over:
                handle_jump()
                visual_effects.add_jump_effect(bird.x, bird.y)
    
    # 更新游戏状态
    if not game_over:
        update_game_state(dt)
        
        # 检查碰撞
        if check_collision():
            handle_collision()
            visual_effects.add_collision_effect(bird.x, bird.y)
        
        # 检查得分
        if check_score():
            handle_score()
            visual_effects.add_score_effect(pipe.x + PIPE_WIDTH // 2, SCREEN_HEIGHT // 2)
    
    # 更新视觉效果
    visual_effects.update(dt)
    
    # 绘制游戏
    draw_game()
    visual_effects.draw(screen)
    
    pygame.display.flip()