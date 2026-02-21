def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Enhanced Breakout Game")
    clock = pygame.time.Clock()
    
    # 初始化游戏组件
    paddle = Paddle()
    ball = Ball()
    bricks = create_bricks()
    particle_system = ParticleSystem()
    ball_trail = BallTrail()
    stats = GameStats()
    sounds = init_sounds()
    
    # 游戏状态
    game_state = "START"  # START, PLAYING, GAME_OVER, WIN
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    if game_state == "START" or game_state in ["GAME_OVER", "WIN"]:
                        reset_game(paddle, ball, bricks, stats)
                        game_state = "PLAYING"
        
        # 根据游戏状态处理不同逻辑
        if game_state == "START":
            show_start_screen(screen)
        elif game_state == "PLAYING":
            # 处理输入
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                paddle.move_left()
            if keys[pygame.K_RIGHT]:
                paddle.move_right()
            
            # 更新游戏逻辑
            ball.update()
            ball_trail.update((ball.x, ball.y))
            particle_system.update()
            
            # 碰撞检测
            if ball.collides_with_paddle(paddle):
                ball.bounce_off_paddle(paddle)
                play_sound(sounds, 'paddle')
                show_game_tip(screen, "Nice hit!", ball.x, ball.y - 20)
            
            for brick in bricks[:]:
                if ball.collides_with_brick(brick):
                    ball.bounce_off_brick(brick)
                    bricks.remove(brick)
                    stats.add_score(10)
                    play_sound(sounds, 'brick')
                    break_brick_animation(screen, brick, particle_system)
                    
                    if not bricks:
                        game_state = "WIN"
                        play_sound(sounds, 'win')
            
            if ball.y > screen.get_height():
                if stats.lose_life():
                    game_state = "GAME_OVER"
                    play_sound(sounds, 'game_over')
                else:
                    ball.reset()
                    play_sound(sounds, 'wall')
            
            # 绘制游戏画面
            screen.fill((0, 0, 0))
            
            # 绘制游戏元素
            for brick in bricks:
                brick.draw(screen)
            
            draw_paddle_with_effect(screen, paddle)
            ball.draw(screen)
            ball_trail.draw(screen, ball.color)
            particle_system.draw(screen)
            draw_game_stats(screen, stats, pygame.font.SysFont('Arial', 20))
            
        elif game_state in ["GAME_OVER", "WIN"]:
            show_game_over_screen(screen, stats, game_state == "WIN")
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

def reset_game(paddle, ball, bricks, stats):
    """重置游戏状态"""
    paddle.reset()
    ball.reset()
    bricks.clear()
    bricks.extend(create_bricks())
    stats.score = 0
    stats.lives = 3
    stats.level = 1

if __name__ == "__main__":
    main()