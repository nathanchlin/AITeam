import pygame
import random
import math
from enum import Enum

class Direction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4

class Tile:
    def __init__(self, value, x, y):
        self.value = value
        self.x = x
        self.y = y
        self.target_x = x
        self.target_y = y
        self.scale = 0.0
        self.target_scale = 1.0
        self.merging = False
        self.new_tile = True
        
    def update(self):
        # 平滑移动到目标位置
        self.x += (self.target_x - self.x) * 0.2
        self.y += (self.target_y - self.y) * 0.2
        
        # 缩放动画
        if self.new_tile:
            self.scale += (self.target_scale - self.scale) * 0.2
            if abs(self.scale - self.target_scale) < 0.01:
                self.scale = self.target_scale
                self.new_tile = False
        elif self.merging:
            self.scale += (1.2 - self.scale) * 0.3
            if self.scale > 1.2:
                self.merging = False
                self.scale = 1.0

class GameRenderer:
    def __init__(self, width=500, height=600):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("2048")
        
        # 游戏区域参数
        self.grid_size = 4
        self.tile_size = 100
        self.tile_margin = 10
        self.grid_x = (width - (self.tile_size + self.tile_margin) * self.grid_size + self.tile_margin) // 2
        self.grid_y = 120
        
        # 颜色定义
        self.colors = {
            0: (205, 193, 180),
            2: (238, 228, 218),
            4: (237, 224, 200),
            8: (242, 177, 121),
            16: (245, 149, 99),
            32: (246, 124, 95),
            64: (246, 94, 59),
            128: (237, 207, 114),
            256: (237, 204, 97),
            512: (237, 200, 80),
            1024: (237, 197, 63),
            2048: (237, 194, 46),
            4096: (60, 58, 50),
            8192: (60, 58, 50),
        }
        
        # 字体
        self.font_large = pygame.font.SysFont('Arial', 55, bold=True)
        self.font_medium = pygame.font.SysFont('Arial', 35, bold=True)
        self.font_small = pygame.font.SysFont('Arial', 25)
        
        # 方块列表
        self.tiles = []
        
        # 动画相关
        self.animation_speed = 0.2
        self.score = 0
        self.game_over = False
        self.game_won = False
        
    def add_tile(self, value, x, y):
        """添加新方块"""
        tile = Tile(value, x, y)
        tile.x = self.grid_x + x * (self.tile_size + self.tile_margin)
        tile.y = self.grid_y + y * (self.tile_size + self.tile_margin)
        self.tiles.append(tile)
        
    def move_tiles(self, direction):
        """移动方块"""
        moved = False
        if direction == Direction.LEFT:
            moved = self.move_left()
        elif direction == Direction.RIGHT:
            moved = self.move_right()
        elif direction == Direction.UP:
            moved = self.move_up()
        elif direction == Direction.DOWN:
            moved = self.move_down()
            
        return moved
        
    def move_left(self):
        """向左移动方块"""
        moved = False
        for y in range(self.grid_size):
            # 获取该行的所有方块
            row = [tile for tile in self.tiles if tile.y == y]
            row.sort(key=lambda tile: tile.x)
            
            # 移动方块
            for i, tile in enumerate(row):
                new_x = 0
                for j in range(i):
                    if row[j].value == tile.value and not row[j].merging:
                        # 合并相同值的方块
                        new_x = row[j].target_x
                        row[j].merging = True
                        row[j].value *= 2
                        self.score += row[j].value
                        self.tiles.remove(tile)
                        moved = True
                        break
                else:
                    # 找到最左边的空位
                    for j in range(i):
                        if row[j].target_x != j:
                            new_x = j
                            break
                    else:
                        new_x = i
                
                if tile.target_x != new_x:
                    tile.target_x = new_x
                    moved = True
        
        return moved
        
    def move_right(self):
        """向右移动方块"""
        moved = False
        for y in range(self.grid_size):
            # 获取该行的所有方块
            row = [tile for tile in self.tiles if tile.y == y]
            row.sort(key=lambda tile: -tile.x)
            
            # 移动方块
            for i, tile in enumerate(row):
                new_x = self.grid_size - 1
                for j in range(i):
                    if row[j].value == tile.value and not row[j].merging:
                        # 合并相同值的方块
                        new_x = row[j].target_x
                        row[j].merging = True
                        row[j].value *= 2
                        self.score += row[j].value
                        self.tiles.remove(tile)
                        moved = True
                        break
                else:
                    # 找到最右边的空位
                    for j in range(i):
                        if row[j].target_x != self.grid_size - 1 - j:
                            new_x = self.grid_size - 1 - j
                            break
                    else:
                        new_x = self.grid_size - 1 - i
                
                if tile.target_x != new_x:
                    tile.target_x = new_x
                    moved = True
        
        return moved
        
    def move_up(self):
        """向上移动方块"""
        moved = False
        for x in range(self.grid_size):
            # 获取该列的所有方块
            column = [tile for tile in self.tiles if tile.x == x]
            column.sort(key=lambda tile: tile.y)
            
            # 移动方块
            for i, tile in enumerate(column):
                new_y = 0
                for j in range(i):
                    if column[j].value == tile.value and not column[j].merging:
                        # 合并相同值的方块
                        new_y = column[j].target_y
                        column[j].merging = True
                        column[j].value *= 2
                        self.score += column[j].value
                        self.tiles.remove(tile)
                        moved = True
                        break
                else:
                    # 找到最上边的空位
                    for j in range(i):
                        if column[j].target_y != j:
                            new_y = j
                            break
                    else:
                        new_y = i
                
                if tile.target_y != new_y:
                    tile.target_y = new_y
                    moved = True
        
        return moved
        
    def move_down(self):
        """向下移动方块"""
        moved = False
        for x in range(self.grid_size):
            # 获取该列的所有方块
            column = [tile for tile in self.tiles if tile.x == x]
            column.sort(key=lambda tile: -tile.y)
            
            # 移动方块
            for i, tile in enumerate(column):
                new_y = self.grid_size - 1
                for j in range(i):
                    if column[j].value == tile.value and not column[j].merging:
                        # 合并相同值的方块
                        new_y = column[j].target_y
                        column[j].merging = True
                        column[j].value *= 2
                        self.score += column[j].value
                        self.tiles.remove(tile)
                        moved = True
                        break
                else:
                    # 找到最下边的空位
                    for j in range(i):
                        if column[j].target_y != self.grid_size - 1 - j:
                            new_y = self.grid_size - 1 - j
                            break
                    else:
                        new_y = self.grid_size - 1 - i
                
                if tile.target_y != new_y:
                    tile.target_y = new_y
                    moved = True
        
        return moved
        
    def add_random_tile(self):
        """在随机空位置添加新方块"""
        empty_cells = []
        for x in range(self.grid_size):
            for y in range(self.grid_size):
                occupied = any(tile.x == x and tile.y == y for tile in self.tiles)
                if not occupied:
                    empty_cells.append((x, y))
        
        if empty_cells:
            x, y = random.choice(empty_cells)
            value = 4 if random.random() < 0.1 else 2
            self.add_tile(value, x, y)
            
    def update(self):
        """更新所有方块的状态"""
        for tile in self.tiles:
            tile.update()
            
    def draw(self):
        """绘制游戏界面"""
        # 背景色
        self.screen.fill((187, 173, 160))
        
        # 绘制标题和分数
        title = self.font_large.render("2048", True, (119, 110, 101))
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 20))
        
        score_text = self.font_medium.render(f"分数: {self.score}", True, (119, 110, 101))
        self.screen.blit(score_text, (self.width // 2 - score_text.get_width() // 2, 70))
        
        # 绘制游戏背景
        pygame.draw.rect(self.screen, (205, 193, 180), 
                        (self.grid_x - self.tile_margin, 
                         self.grid_y - self.tile_margin,
                         (self.tile_size + self.tile_margin) * self.grid_size + self.tile_margin,
                         (self.tile_size + self.tile_margin) * self.grid_size + self.tile_margin),
                         border_radius=6)
        
        # 绘制所有方块
        for tile in self.tiles:
            # 计算方块位置
            x = self.grid_x + tile.x * (self.tile_size + self.tile_margin)
            y = self.grid_y + tile.y * (self.tile_size + self.tile_margin)
            
            # 应用缩放
            size = int(self.tile_size * tile.scale)
            offset = (self.tile_size - size) // 2
            
            # 绘制方块
            color = self.colors.get(tile.value, (60, 58, 50))
            pygame.draw.rect(self.screen, color,
                           (x + offset, y + offset, size, size),
                           border_radius=3)
            
            # 绘制数字
            text_color = (249, 246, 242) if tile.value > 4 else (119, 110, 101)
            font_size = 55 if tile.value < 100 else 45 if tile.value < 1000 else 35
            font = pygame.font.SysFont('Arial', font_size, bold=True)
            text = font.render(str(tile.value), True, text_color)
            text_rect = text.get_rect(center=(x + self.tile_size // 2, y + self.tile_size // 2))
            self.screen.blit(text, text_rect)
        
        # 游戏结束或胜利提示
        if self.game_over:
            self.draw_game_over()
        elif self.game_won:
            self.draw_game_won()
            
    def draw_game_over(self):
        """绘制游戏结束画面"""
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 180))
        self.screen.blit(overlay, (0, 0))
        
        game_over_text = self.font_large.render("游戏结束!", True, (119, 110, 101))
        self.screen.blit(game_over_text, 
                        (self.width // 2 - game_over_text.get_width() // 2, 
                         self.height // 2 - 50))
        
        restart_text = self.font_small.render("按 R 键重新开始", True, (119, 110, 101))
        self.screen.blit(restart_text, 
                        (self.width // 2 - restart_text.get_width() // 2, 
                         self.height // 2 + 20))
        
    def draw_game_won(self):
        """绘制游戏胜利画面"""
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 180))
        self.screen.blit(overlay, (0, 0))
        
        won_text = self.font_large.render("你赢了!", True, (119, 110, 101))
        self.screen.blit(won_text, 
                        (self.width // 2 - won_text.get_width() // 2, 
                         self.height // 2 - 50))
        
        continue_text = self.font_small.render("按 C 键继续游戏", True, (119, 110, 101))
        self.screen.blit(continue_text, 
                        (self.width // 2 - continue_text.get_width() // 2, 
                         self.height // 2 + 20))
        
    def restart(self):
        """重新开始游戏"""
        self.tiles = []
        self.score = 0
        self.game_over = False
        self.game_won = False
        self.add_random_tile()
        self.add_random_tile()