import pygame
import random
import json
import os

# 初始化Pygame
pygame.init()

# 游戏设置
WIDTH, HEIGHT = 600, 600
GRID_SIZE = 20
CELL_SIZE = WIDTH // GRID_SIZE
FPS = 10

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# 分数设置
FOOD_BASE_SCORE = 10  # 基础食物分值
SPECIAL_FOOD_SCORE = 50  # 特殊食物分值
SPECIAL_FOOD_PROBABILITY = 0.2  # 特殊食物出现概率

class ScoreSystem:
    def __init__(self):
        self.current_score = 0
        self.high_score = self.load_high_score()
    
    def load_high_score(self):
        """从文件加载最高分"""
        try:
            if os.path.exists("snake_highscore.json"):
                with open("snake_highscore.json", "r") as f:
                    data = json.load(f)
                    return data.get("high_score", 0)
        except:
            pass
        return 0
    
    def save_high_score(self):
        """保存最高分到文件"""
        try:
            with open("snake_highscore.json", "w") as f:
                json.dump({"high_score": self.high_score}, f)
        except:
            pass
    
    def add_score(self, food_type="normal"):
        """根据食物类型添加分数"""
        if food_type == "special":
            self.current_score += SPECIAL_FOOD_SCORE
        else:
            self.current_score += FOOD_BASE_SCORE
        
        # 更新最高分
        if self.current_score > self.high_score:
            self.high_score = self.current_score
            self.save_high_score()
    
    def reset_score(self):
        """重置当前分数"""
        self.current_score = 0
    
    def draw_score(self, screen, font):
        """在屏幕上绘制分数"""
        score_text = font.render(f"分数: {self.current_score}", True, BLACK)
        high_score_text = font.render(f"最高分: {self.high_score}", True, BLACK)
        screen.blit(score_text, (10, 10))
        screen.blit(high_score_text, (WIDTH - 150, 10))

class Snake:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.positions = [(GRID_SIZE // 2, GRID_SIZE // 2)]
        self.direction = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
        self.grow = False
    
    def get_head_position(self):
        return self.positions[0]
    
    def update(self):
        cur = self.get_head_position()
        x, y = self.direction
        new = ((cur[0] + x) % GRID_SIZE, (cur[1] + y) % GRID_SIZE)
        
        if new in self.positions[3:]:
            return False  # 游戏结束
        
        self.positions.insert(0, new)
        
        if not self.grow:
            self.positions.pop()
        else:
            self.grow = False
        
        return True
    
    def reset_direction(self, direction):
        # 防止蛇直接掉头
        if (self.direction[0] * -1, self.direction[1] * -1) != direction:
            self.direction = direction
    
    def grow_snake(self):
        self.grow = True
    
    def draw(self, surface):
        for p in self.positions:
            pygame.draw.rect(surface, GREEN, (p[0] * CELL_SIZE, p[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))

class Food:
    def __init__(self):
        self.position = (0, 0)
        self.type = "normal"
        self.randomize_position()
    
    def randomize_position(self):
        self.position = (random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1))
        # 随机决定是否生成特殊食物
        self.type = "special" if random.random() < SPECIAL_FOOD_PROBABILITY else "normal"
    
    def draw(self, surface):
        color = YELLOW if self.type == "special" else RED
        pygame.draw.rect(surface, color, 
                        (self.position[0] * CELL_SIZE, self.position[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("贪吃蛇游戏")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont('arial', 20)
    
    snake = Snake()
    food = Food()
    score_system = ScoreSystem()
    game_over = False
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            
            if event.type == pygame.KEYDOWN and not game_over:
                if event.key == pygame.K_UP:
                    snake.reset_direction((0, -1))
                elif event.key == pygame.K_DOWN:
                    snake.reset_direction((0, 1))
                elif event.key == pygame.K_LEFT:
                    snake.reset_direction((-1, 0))
                elif event.key == pygame.K_RIGHT:
                    snake.reset_direction((1, 0))
            
            if event.type == pygame.KEYDOWN and game_over:
                if event.key == pygame.K_SPACE:
                    # 重新开始游戏
                    snake.reset()
                    food.randomize_position()
                    score_system.reset_score()
                    game_over = False
        
        if not game_over:
            # 更新蛇的位置
            if not snake.update():
                game_over = True
            
            # 检查是否吃到食物
            if snake.get_head_position() == food.position:
                snake.grow_snake()
                score_system.add_score(food.type)
                food.randomize_position()
                # 确保食物不会生成在蛇身上
                while food.position in snake.positions:
                    food.randomize_position()
        
        # 绘制游戏画面
        screen.fill(WHITE)
        
        # 绘制网格线（可选）
        for x in range(0, WIDTH, CELL_SIZE):
            pygame.draw.line(screen, (200, 200, 200), (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, CELL_SIZE):
            pygame.draw.line(screen, (200, 200, 200), (0, y), (WIDTH, y))
        
        # 绘制游戏元素
        snake.draw(screen)
        food.draw(screen)
        score_system.draw_score(screen, font)
        
        # 游戏结束提示
        if game_over:
            game_over_text = font.render("游戏结束! 按空格键重新开始", True, BLACK)
            screen.blit(game_over_text, (WIDTH // 2 - 150, HEIGHT // 2))
        
        pygame.display.update()
        clock.tick(FPS)

if __name__ == "__main__":
    main()