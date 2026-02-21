import pygame
import sys

# 初始化Pygame
pygame.init()

# 游戏设置
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
FPS = 60

# 创建窗口
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Bird")
clock = pygame.time.Clock()

# 创建小鸟
bird = Bird(100, SCREEN_HEIGHT // 2)

# 游戏主循环
running = True
while running:
    # 事件处理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bird.jump()
    
    # 更新游戏状态
    bird.update()
    
    # 检查边界碰撞
    if bird.y < 0 or bird.y > SCREEN_HEIGHT:
        # 游戏结束逻辑
        running = False
    
    # 绘制
    screen.fill((135, 206, 235))  # 天空蓝背景
    bird.draw(screen)
    
    # 更新显示
    pygame.display.flip()
    clock.tick(FPS)

# 退出游戏
pygame.quit()
sys.exit()