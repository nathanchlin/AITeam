import pygame
import random
import time

# 游戏常量
GRID_WIDTH = 10
GRID_HEIGHT = 20
CELL_SIZE = 30
SCREEN_WIDTH = GRID_WIDTH * CELL_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * CELL_SIZE
FPS = 60

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

# 方块形状定义
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[1, 1, 1], [0, 1, 0]],  # T
    [[1, 1, 1], [1, 0, 0]],  # L
    [[1, 1, 1], [0, 0, 1]],  # J
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 1, 0], [0, 1, 1]]   # Z
]

# 方块颜色
SHAPE_COLORS = [CYAN, YELLOW, MAGENTA, ORANGE, BLUE, GREEN, RED]

class Tetromino:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.shape_index = random.randint(0, len(SHAPES) - 1)
        self.shape = SHAPES[self.shape_index]
        self.color = SHAPE_COLORS[self.shape_index]
        self.rotation = 0
        
    def rotate(self):
        # 顺时针旋转90度
        rotated = [[self.shape[y][x] for y in range(len(self.shape)-1, -1, -1)] 
                  for x in range(len(self.shape[0]))]
        return rotated
    
    def get_cells(self):
        # 获取方块占据的所有格子坐标
        cells = []
        for y, row in enumerate(self.shape):
            for x, cell in enumerate(row):
                if cell:
                    cells.append((self.x + x, self.y + y))
        return cells

class TetrisGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("俄罗斯方块")
        self.clock = pygame.time.Clock()
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.score = 0
        self.lines_cleared = 0
        self.level = 1
        self.fall_time = 0
        self.fall_speed = 1000  # 初始下落速度(毫秒)
        self.fall_fast = False
        self.game_over = False
        
    def new_piece(self):
        return Tetromino(GRID_WIDTH // 2 - 1, 0)
    
    def valid_move(self, piece, dx=0, dy=0, rotation=None):
        # 检查移动是否有效
        test_shape = rotation if rotation is not None else piece.shape
        for y, row in enumerate(test_shape):
            for x, cell in enumerate(row):
                if cell:
                    new_x = piece.x + x + dx
                    new_y = piece.y + y + dy
                    
                    # 检查边界
                    if new_x < 0 or new_x >= GRID_WIDTH or new_y >= GRID_HEIGHT:
                        return False
                    
                    # 检查碰撞
                    if new_y >= 0 and self.grid[new_y][new_x]:
                        return False
        return True
    
    def lock_piece(self):
        # 将当前方块固定到网格中
        for x, y in self.current_piece.get_cells():
            if y >= 0:
                self.grid[y][x] = self.current_piece.shape_index + 1
        
        # 检查是否有完整的行
        self.clear_lines()
        
        # 生成新方块
        self.current_piece = self.next_piece
        self.next_piece = self.new_piece()
        
        # 检查游戏是否结束
        if not self.valid_move(self.current_piece):
            self.game_over = True
    
    def clear_lines(self):
        # 检查并清除完整的行
        lines_to_clear = []
        for y in range(GRID_HEIGHT):
            if all(self.grid[y]):
                lines_to_clear.append(y)
        
        # 清除完整的行
        for y in lines_to_clear:
            del self.grid[y]
            self.grid.insert(0, [0 for _ in range(GRID_WIDTH)])
        
        # 更新分数和等级
        if lines_to_clear:
            self.lines_cleared += len(lines_to_clear)
            self.score += [40, 100, 300, 1200][len(lines_to_clear) - 1] * self.level
            self.level = 1 + self.lines_cleared // 10
            self.fall_speed = max(100, 1000 - (self.level - 1) * 100)
    
    def update(self, dt):
        if self.game_over:
            return
        
        # 处理方块下落
        self.fall_time += dt
        fall_interval = 50 if self.fall_fast else self.fall_speed
        
        if self.fall_time >= fall_interval:
            if self.valid_move(self.current_piece, dy=1):
                self.current_piece.y += 1
            else:
                self.lock_piece()
            self.fall_time = 0
    
    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        # 左右移动
        if keys[pygame.K_LEFT] and self.valid_move(self.current_piece, dx=-1):
            self.current_piece.x -= 1
        if keys[pygame.K_RIGHT] and self.valid_move(self.current_piece, dx=1):
            self.current_piece.x += 1
        
        # 加速下落
        self.fall_fast = keys[pygame.K_DOWN]
        
        # 旋转
        if keys[pygame.K_UP]:
            rotated = self.current_piece.rotate()
            if self.valid_move(self.current_piece, rotation=rotated):
                self.current_piece.shape = rotated
    
    def draw(self):
        self.screen.fill(BLACK)
        
        # 绘制网格
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y][x]:
                    color = SHAPE_COLORS[self.grid[y][x] - 1]
                    pygame.draw.rect(self.screen, color, 
                                   (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        
        # 绘制当前方块
        for x, y in self.current_piece.get_cells():
            if y >= 0:
                pygame.draw.rect(self.screen, self.current_piece.color,
                               (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        
        # 绘制网格线
        for x in range(GRID_WIDTH + 1):
            pygame.draw.line(self.screen, GRAY, (x * CELL_SIZE, 0), 
                            (x * CELL_SIZE, SCREEN_HEIGHT), 1)
        for y in range(GRID_HEIGHT + 1):
            pygame.draw.line(self.screen, GRAY, (0, y * CELL_SIZE), 
                            (SCREEN_WIDTH, y * CELL_SIZE), 1)
        
        # 显示分数和等级
        font = pygame.font.SysFont('Arial', 20)
        score_text = font.render(f"分数: {self.score}", True, WHITE)
        level_text = font.render(f"等级: {self.level}", True, WHITE)
        lines_text = font.render(f"行数: {self.lines_cleared}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(level_text, (10, 40))
        self.screen.blit(lines_text, (10, 70))
        
        if self.game_over:
            game_over_text = font.render("游戏结束!", True, RED)
            self.screen.blit(game_over_text, 
                           (SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2))
        
        pygame.display.flip()
    
    def run(self):
        running = True
        dt = 0
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and not self.game_over:
                        # 硬降（直接落到底部）
                        while self.valid_move(self.current_piece, dy=1):
                            self.current_piece.y += 1
                        self.lock_piece()
                    elif event.key == pygame.K_r and self.game_over:
                        # 重新开始游戏
                        self.__init__()
            
            self.handle_input()
            self.update(dt)
            self.draw()
            dt = self.clock.tick(FPS)
        
        pygame.quit()

if __name__ == "__main__":
    game = TetrisGame()
    game.run()