def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("俄罗斯方块")
    clock = pygame.time.Clock()
    
    # 初始化游戏组件
    game_board = GameBoard(10, 20)
    game_controller = GameController(game_board)
    game_renderer = GameRenderer(screen)
    
    running = True
    while running:
        dt = clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q and game_controller.state_manager.get_state() == GameState.MENU:
                    running = False
                elif event.key == pygame.K_s and game_controller.state_manager.get_state() == GameState.MENU:
                    game_controller.start_game()
                else:
                    game_controller.handle_input(event)
        
        # 更新游戏逻辑
        game_controller.update(dt)
        
        # 渲染游戏
        game_renderer.render()
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    main()