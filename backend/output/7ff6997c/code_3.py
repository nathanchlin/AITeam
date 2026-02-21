def game_loop():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("忍者必须死 - 跑酷游戏")
    clock = pygame.time.Clock()
    
    # 创建忍者角色
    ninja = Ninja(100, 300)
    
    # 游戏主循环
    running = True
    while running:
        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    ninja.jump()
                elif event.key == pygame.K_DOWN:
                    ninja.slide()
                elif event.key == pygame.K_x:
                    ninja.attack()
                    
        # 获取按键状态
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            ninja.vel_x = -ninja.move_speed
            ninja.facing_right = False
        elif keys[pygame.K_RIGHT]:
            ninja.vel_x = ninja.move_speed
            ninja.facing_right = True
        else:
            ninja.vel_x = 0
            
        # 更新游戏状态
        ninja.update()
        
        # 绘制
        screen.fill((135, 206, 235))  # 天蓝色背景
        
        # 绘制地面
        pygame.draw.rect(screen, (101, 67, 33), (0, 364, 800, 236))
        
        # 绘制忍者
        ninja.draw(screen)
        
        # 更新显示
        pygame.display.flip()
        clock.tick(60)
        
    pygame.quit()

# 启动游戏
if __name__ == "__main__":
    game_loop()