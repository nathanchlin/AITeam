import pygame
import sys

# 初始化Pygame
pygame.init()

# 设置窗口
screen_width = 800
screen_height = 400
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("绿色忍者跑酷")

# 创建时钟对象
clock = pygame.time.Clock()

# 创建忍者
ninja = Ninja(100, 300)

# 游戏主循环
running = True
while running:
    # 处理事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                ninja.jump()
            elif event.key == pygame.K_x:
                ninja.attack()
        elif event.type == pygame.USEREVENT + 1:
            # 攻击动画结束
            ninja.animation_state = "run"
            pygame.time.set_timer(pygame.USEREVENT + 1, 0)  # 停止计时器
    
    # 更新
    ninja.update()
    
    # 处理输入
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        ninja.x -= 5
        ninja.facing_right = False
        if not ninja.jumping:
            ninja.animation_state = "run"
    elif keys[pygame.K_RIGHT]:
        ninja.x += 5
        ninja.facing_right = True
        if not ninja.jumping:
            ninja.animation_state = "run"
    elif not ninja.jumping and ninja.animation_state != "attack":
        ninja.animation_state = "idle"
    
    # 绘制背景
    screen.fill((135, 206, 235))  # 天蓝色背景
    
    # 绘制地面
    pygame.draw.rect(screen, (100, 100, 100), (0, 348, screen_width, 52))
    
    # 绘制忍者
    ninja.draw(screen)
    
    # 更新显示
    pygame.display.flip()
    
    # 控制帧率
    clock.tick(60)

# 退出游戏
pygame.quit()
sys.exit()