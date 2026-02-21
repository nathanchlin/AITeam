# 初始化pygame
pygame.init()
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("打砖块游戏")

# 创建挡板
paddle_width = 100
paddle_height = 20
paddle_rect = pygame.Rect(screen_width // 2 - paddle_width // 2, 
                         screen_height - 40, 
                         paddle_width, 
                         paddle_height)

# 创建挡板控制器
paddle_controller = PaddleController(paddle_speed=10)

# 游戏主循环
clock = pygame.time.Clock()
running = True

while running:
    # 事件处理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        else:
            paddle_controller.handle_event(event)
    
    # 更新挡板位置
    paddle_rect = paddle_controller.update(paddle_rect, screen_width)
    
    # 渲染
    screen.fill((0, 0, 0))
    pygame.draw.rect(screen, (255, 255, 255), paddle_rect)
    pygame.display.flip()
    
    # 控制帧率
    clock.tick(60)

pygame.quit()
sys.exit()