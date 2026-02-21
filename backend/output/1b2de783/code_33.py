# 游戏主循环示例
def game_loop():
    pygame.init()
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("太空射击游戏")
    clock = pygame.time.Clock()
    
    # 初始化陨石管理器
    asteroid_manager = AsteroidManager(width, height)
    
    # 玩家飞船
    player = Player(width // 2, height // 2)
    
    running = True
    while running:
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # 处理玩家输入
        
        # 更新游戏状态
        player.update()
        asteroid_manager.update()
        
        # 碰撞检测
        player_rect = player.get_rect()
        hit_asteroid = asteroid_manager.check_collision(player_rect)
        if hit_asteroid:
            # 处理玩家与陨石碰撞
            player.take_damage(10)
            # 可以添加爆炸效果等
        
        # 绘制
        screen.fill((0, 0, 20))  # 深蓝色背景
        player.draw(screen)
        asteroid_manager.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()