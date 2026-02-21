def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("1942 风格射击游戏")
    clock = pygame.time.Clock()
    
    # 初始化游戏对象
    player = Player(400, 500)
    bullet_manager = BulletManager()
    enemies = []
    
    # 游戏状态
    running = True
    score = 0
    enemy_spawn_timer = 0
    
    while running:
        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.fire(bullet_manager)
                elif event.key == pygame.K_p:  # P键升级武器
                    player.power_level = min(player.power_level + 1, 3)
        
        # 获取按键状态
        keys = pygame.key.get_pressed()
        
        # 更新游戏对象
        player.update(keys)
        bullet_manager.update()
        
        # 生成敌人
        enemy_spawn_timer += 1
        if enemy_spawn_timer > 60:  # 每秒生成一个敌人
            enemy_x = random.randint(0, screen.get_width() - 30)
            enemy_type = random.choice(["normal", "normal", "zigzag", "fast"])
            enemies.append(Enemy(enemy_x, -30, enemy_type))
            enemy_spawn_timer = 0
        
        # 更新敌人
        for enemy in enemies[:]:
            enemy.update(player.x, player.y)
            enemy.fire(bullet_manager)
            
            # 移除超出屏幕的敌人
            if enemy.y > screen.get_height():
                enemies.remove(enemy)
        
        # 碰撞检测
        bullet_manager.check_collisions(player.get_rect(), enemies)
        
        # 绘制
        screen.fill((0, 0, 30))  # 深蓝色背景
        
        # 绘制星空背景
        for _ in range(50):
            x = random.randint(0, screen.get_width())
            y = random.randint(0, screen.get_height())
            pygame.draw.circle(screen, (255, 255, 255), (x, y), 1)
        
        player.draw(screen)
        
        for enemy in enemies:
            enemy.draw(screen)
        
        bullet_manager.draw(screen)
        
        # 显示分数和武器等级
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        power_text = font.render(f"Power: {player.power_level}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
        screen.blit(power_text, (10, 50))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    import math
    import random
    main()