import random
import time

class FoodGenerator:
    def __init__(self, game_width, game_height, cell_size):
        """
        初始化食物生成器
        
        参数:
            game_width: 游戏区域宽度(像素)
            game_height: 游戏区域高度(像素)
            cell_size: 每个格子的大小(像素)
        """
        self.game_width = game_width
        self.game_height = game_height
        self.cell_size = cell_size
        self.grid_width = game_width // cell_size
        self.grid_height = game_height // cell_size
        
    def generate_food(self, snake_body):
        """
        生成不与蛇身重叠的食物位置
        
        参数:
            snake_body: 蛇身体的坐标列表，每个坐标是(x, y)元组
            
        返回:
            食物的坐标 (x, y)
        """
        # 计算所有可能的格子位置
        all_positions = []
        for x in range(self.grid_width):
            for y in range(self.grid_height):
                all_positions.append((x, y))
        
        # 移除蛇身占据的位置
        occupied_positions = set(snake_body)
        available_positions = [pos for pos in all_positions if pos not in occupied_positions]
        
        # 如果没有可用位置(蛇占满整个屏幕)，返回None
        if not available_positions:
            return None
            
        # 随机选择一个可用位置
        food_position = random.choice(available_positions)
        
        # 将网格坐标转换为像素坐标
        food_x = food_position[0] * self.cell_size
        food_y = food_position[1] * self.cell_size
        
        return (food_x, food_y)