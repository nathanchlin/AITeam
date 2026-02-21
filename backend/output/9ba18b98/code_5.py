def main():
    # 初始化Pygame
    pygame.init()
    
    # 游戏参数
    WIDTH, HEIGHT = 10, 20
    CELL_SIZE = 30
    SCREEN_WIDTH = WIDTH * CELL_SIZE
    SCREEN_HEIGHT = HEIGHT * CELL_SIZE
    
    # 创建屏幕
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("俄罗斯方块")
    
    # 创建游戏实例
    game = Tetris(WIDTH, HEIGHT, CELL_SIZE)
    
    # 游戏时钟
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 500  # 毫秒
    
    # 游戏主循环
    running = True
    while running:
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    game.move_piece(-1, 0)
                elif event.key == pygame.K_RIGHT:
                    game.move_piece(1, 0)
                elif event.key == pygame.K_DOWN:
                    game.move_piece(0, 1)
                elif event.key == pygame.K_UP:
                    game.rotate_piece()
                elif event.key == pygame.K_SPACE and game.game_over:
                    # 重新开始游戏
                    game = Tetris(WIDTH, HEIGHT, CELL_SIZE)
        
        # 更新游戏状态
        fall_time += clock.get_rawtime()
        clock.tick()
        
        if fall_time >= fall_speed:
            game.update()
            fall_time = 0
        
        # 绘制游戏画面
        screen.fill((50, 50, 50))
        game.draw(screen)
        
        # 显示分数
        font = pygame.font.SysFont(None, 24)
        score_text = font.render(f"Score: {game.score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
        
        # 更新显示
        pygame.display.flip()
    
    # 退出游戏
    pygame.quit()

if __name__ == "__main__":
    main()