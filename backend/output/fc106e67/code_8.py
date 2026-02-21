def main():
    pygame.init()
    screen_width, screen_height = 800, 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("忍者必须死")
    clock = pygame.time.Clock()
    
    # 初始化游戏组件
    background = init_background(screen_width, screen_height)
    particle_system = ParticleSystem()
    ui = UI(screen_width, screen_height)
    ninja = Ninja(100, screen_height - 100)
    
    running = True
    game_speed = 1.0
    
    while running:
        dt = clock.tick(60) / 1000.0  # 转换为秒
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    ninja.jump()
                elif event.key == pygame.K_x:
                    ninja.attack()
                    add_attack_effect(particle_system, (ninja.x + (40 if ninja.facing_right else -40), ninja.y))
        
        # 更新游戏状态
        ninja.update(dt)
        background.update(dt, game_speed)
        particle_system.update(dt)
        
        # 添加忍者移动效果
        if ninja.jumping:
            add_jump_effect(particle_system, (ninja.x, ninja.y + ninja.height // 2))
            ninja.jumping = False
            
        add_ninja_trail(particle_system, (ninja.x, ninja.y))
        
        # 绘制
        screen.fill((0, 0, 0))
        background.draw(screen)
        particle_system.draw(screen)
        ninja.draw(screen)
        ui.draw(screen)
        
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    main()