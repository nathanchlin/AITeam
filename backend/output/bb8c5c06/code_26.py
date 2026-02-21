import pygame
import random

# 游戏常量
GRID_WIDTH = 20
GRID_HEIGHT = 15
CELL_SIZE = 30
SCREEN_WIDTH = GRID_WIDTH * CELL_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * CELL_SIZE
SPEED = 10

# 颜色定义
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

def draw_game(screen, snake, food, score):
    """绘制游戏画面"""
    screen.fill(BLACK)
    
    # 绘制网格线（可选）
    for x in range(0, SCREEN_WIDTH, CELL_SIZE):
        pygame.draw.line(screen, (50, 50, 50), (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, CELL_SIZE):
        pygame.draw.line(screen, (50, 50, 50), (0, y), (SCREEN_WIDTH, y))
    
    # 绘制蛇
    for i, segment in enumerate(snake):
        color = GREEN if i == 0 else (0, 200, 0)  # 蛇头颜色稍亮
        rect = pygame.Rect(segment[0] * CELL_SIZE, segment[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, BLACK, rect, 1)  # 边框
    
    # 绘制食物
    food_rect = pygame.Rect(food[0] * CELL_SIZE, food[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(screen, RED, food_rect)
    pygame.draw.rect(screen, BLACK, food_rect, 1)
    
    # 绘制分数
    font = pygame.font.SysFont(None, 36)
    score_text = font.render(f"得分: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))
    
    pygame.display.flip()

def draw_game_over(screen, score):
    """绘制游戏结束画面"""
    # 创建半透明覆盖层
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(128)  # 透明度
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))
    
    # 设置字体
    font_large = pygame.font.SysFont(None, 72)
    font_medium = pygame.font.SysFont(None, 36)
    
    # 游戏结束文本
    game_over_text = font_large.render("游戏结束", True, (255, 255, 255))
    game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
    screen.blit(game_over_text, game_over_rect)
    
    # 分数文本
    score_text = font_medium.render(f"得分: {score}", True, (255, 255, 255))
    score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
    screen.blit(score_text, score_rect)
    
    # 重新开始提示
    restart_text = font_medium.render("按空格键重新开始", True, (255, 255, 255))
    restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
    screen.blit(restart_text, restart_rect)
    
    # 更新显示
    pygame.display.flip()

def check_collision(snake):
    """检查碰撞条件"""
    # 获取蛇头位置
    head = snake[0]
    
    # 检查是否撞墙
    if (head[0] < 0 or head[0] >= GRID_WIDTH or 
        head[1] < 0 or head[1] >= GRID_HEIGHT):
        return True
    
    # 检查是否撞到自己（蛇身长度大于1时检查）
    if len(snake) > 2 and head in snake[1:]:
        return True
    
    return False

def reset_game():
    """重置游戏状态"""
    # 初始蛇的位置（水平居中，垂直居上）
    snake = [
        [GRID_WIDTH // 2, GRID_HEIGHT // 2],
        [GRID_WIDTH // 2 - 1, GRID_HEIGHT // 2],
        [GRID_WIDTH // 2 - 2, GRID_HEIGHT // 2]
    ]
    
    # 初始移动方向
    direction = [1, 0]  # 向右移动
    
    # 生成第一个食物
    food = generate_food(snake)
    
    # 初始分数
    score = 0
    
    return snake, direction, food, score

def generate_food(snake):
    """生成食物，确保不在蛇身上"""
    while True:
        food = [
            random.randint(0, GRID_WIDTH - 1),
            random.randint(0, GRID_HEIGHT - 1)
        ]
        if food not in snake:
            return food

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("贪吃蛇游戏")
    clock = pygame.time.Clock()
    
    # 初始化游戏状态
    snake, direction, food, score = reset_game()
    game_over = False
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if not game_over:
                # 处理方向键输入
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP and direction != [0, 1]:
                        direction = [0, -1]
                    elif event.key == pygame.K_DOWN and direction != [0, -1]:
                        direction = [0, 1]
                    elif event.key == pygame.K_LEFT and direction != [1, 0]:
                        direction = [-1, 0]
                    elif event.key == pygame.K_RIGHT and direction != [-1, 0]:
                        direction = [1, 0]
            else:
                # 游戏结束后按空格键重新开始
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        snake, direction, food, score = reset_game()
                        game_over = False
        
        if not game_over:
            # 移动蛇
            new_head = [snake[0][0] + direction[0], snake[0][1] + direction[1]]
            snake.insert(0, new_head)
            
            # 检查是否吃到食物
            if snake[0] == food:
                score += 1
                food = generate_food(snake)
            else:
                snake.pop()
            
            # 检查碰撞
            if check_collision(snake):
                game_over = True
        
        # 绘制游戏
        draw_game(screen, snake, food, score)
        
        # 如果游戏结束，绘制游戏结束画面
        if game_over:
            draw_game_over(screen, score)
        
        # 控制游戏速度
        clock.tick(SPEED)
    
    pygame.quit()

if __name__ == "__main__":
    main()