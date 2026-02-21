def game_loop():
    # 初始化
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("1942风格游戏")
    clock = pygame.time.Clock()
    
    # 创建游戏对象
    player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
    collision_manager = OptimizedCollisionManager()
    collision_manager.set_player(player)
    
    # 游戏主循环
    running = True
    while running:
        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # 发射子弹
                    bullet = Bullet(player.x + player.width // 2, player.y, "up", "player")
                    collision_manager.add_bullet(bullet)
        
        # 获取按键状态
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.move("left")
        if keys[pygame.K_RIGHT]:
            player.move("right")
        if keys[pygame.K_UP]:
            player.move("up")
        if keys[pygame.K_DOWN]:
            player.move("down")
        
        # 生成敌机
        if random.randint(1, 100) < 2:
            enemy = Enemy(random.randint(0, SCREEN_WIDTH - 35), -30)
            collision_manager.add_enemy(enemy)
        
        # 敌机发射子弹
        for enemy in collision_manager.enemies:
            if enemy.active and random.randint(1, 100) < 1:
                bullet = Bullet(enemy.x + enemy.width // 2, enemy.y + enemy.height, "down", "enemy")
                collision_manager.add_bullet(bullet)
        
        # 更新游戏对象
        player.update()
        
        for enemy in collision_manager.enemies[:]:
            enemy.update()
            if not enemy.active:
                collision_manager.enemies.remove(enemy)
        
        for bullet in collision_manager.bullets[:]:
            bullet.update()
            if not bullet.active:
                collision_manager.bullets.remove(bullet)
        
        # 更新碰撞检测
        collision_manager.update()
        
        # 绘制
        screen.fill((0, 0, 0))
        player.draw(screen)
        
        for enemy in collision_manager.enemies:
            enemy.draw(screen)
        
        for bullet in collision_manager.bullets:
            bullet.draw(screen)
        
        # 显示分数和生命值
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Score: {player.score}", True, (255, 255, 255))
        health_text = font.render(f"Health: {player.health}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
        screen.blit(health_text, (10, 50))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

# 游戏常量
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600