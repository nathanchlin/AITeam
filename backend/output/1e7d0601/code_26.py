def main():
    pygame.init()
    screen_width, screen_height = 800, 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("1942 Style Air Combat")
    clock = pygame.time.Clock()
    
    game_controller = GameController(screen_width, screen_height)
    running = True
    
    while running:
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            game_controller.handle_events(event)
            
        # 获取按键状态
        keys = pygame.key.get_pressed()
        
        # 更新游戏状态
        game_controller.update(keys)
        
        # 绘制
        screen.fill((0, 0, 20))  # 深蓝色背景
        game_controller.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)  # 60 FPS
        
    pygame.quit()

if __name__ == "__main__":
    main()