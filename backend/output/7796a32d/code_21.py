# 初始化游戏
pygame.init()
screen_width, screen_height = 400, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("是男人就下100层")

# 创建平台生成器
platform_generator = PlatformGenerator(screen_width, screen_height)

# 生成第一层
platform_generator.generate_floor(1)

# 游戏主循环
clock = pygame.time.Clock()
running = True
dt = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
    # 更新平台和障碍物
    platform_generator.update(dt)
    
    # 绘制
    screen.fill((0, 0, 0))
    
    # 绘制平台
    for platform in platform_generator.platforms:
        color = (100, 100, 100)  # 默认灰色
        if platform.type == PlatformType.MOVING:
            color = (100, 150, 255)  # 蓝色移动平台
        elif platform.type == PlatformType.BREAKING:
            color = (255, 150, 100)  # 橙色断裂平台
        elif platform.type == PlatformType.SPRING:
            color = (100, 255, 150)  # 绿色弹跳平台
            
        pygame.draw.rect(screen, color, platform.get_rect())
    
    # 绘制障碍物
    for obstacle in platform_generator.obstacles:
        if obstacle.type == ObstacleType.SPIKE:
            pygame.draw.polygon(screen, (255, 0, 0), [
                (obstacle.x + 10, obstacle.y),
                (obstacle.x, obstacle.y + 20),
                (obstacle.x + 20, obstacle.y + 20)
            ])
        elif obstacle.type == ObstacleType.MOVING_SPIKE:
            pygame.draw.polygon(screen, (255, 100, 0), [
                (obstacle.x + 10, obstacle.y),
                (obstacle.x, obstacle.y + 20),
                (obstacle.x + 20, obstacle.y + 20)
            ])
        elif obstacle.type == ObstacleType.WIND:
            pygame.draw.rect(screen, (200, 200, 255, 128), obstacle.get_rect())
    
    pygame.display.flip()
    dt = clock.tick(60) / 1000.0
    
    # 当玩家到达底部时生成新楼层
    # 这里需要根据实际游戏逻辑实现
    
pygame.quit()