def break_brick_animation(screen, brick, particle_system):
    """砖块破坏动画"""
    # 添加粒子效果
    particle_system.add_particles(
        brick.x + brick.width // 2,
        brick.y + brick.height // 2,
        brick.color,
        15
    )
    
    # 闪烁效果
    for i in range(3):
        screen.fill((255, 255, 255), brick.rect)
        pygame.display.flip()
        pygame.time.delay(50)
        screen.fill((0, 0, 0), brick.rect)
        pygame.display.flip()
        pygame.time.delay(50)