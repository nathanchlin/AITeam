class OptimizedFoodGenerator:
    def __init__(self, game_width, game_height, cell_size):
        """
        初始化优化后的食物生成器
        """
        self.game_width = game_width
        self.game_height = game_height
        self.cell_size = cell_size
        self.grid_width = game_width // cell_size
        self.grid_height = game_height // cell_size
        
    def generate_food(self, snake_body):
        """
        生成不与蛇身重叠的食物位置(优化版)
        
        参数:
            snake_body: 蛇身体的坐标列表，每个坐标是(x, y)元组
            
        返回:
            食物的坐标 (x, y) 或 None(如果没有可用位置)
        """
        # 将蛇身体坐标转换为网格坐标
        snake_grid_positions = {(x // self.cell_size, y // self.cell_size) 
                              for x, y in snake_body}
        
        # 计算可用位置的数量
        total_positions = self.grid_width * self.grid_height
        occupied_positions = len(snake_grid_positions)
        available_positions = total_positions - occupied_positions
        
        # 如果没有可用位置，返回None
        if available_positions <= 0:
            return None
            
        # 随机尝试生成食物位置，直到找到有效位置
        max_attempts = 100  # 防止无限循环
        for _ in range(max_attempts):
            # 随机生成网格坐标
            grid_x = random.randint(0, self.grid_width - 1)
            grid_y = random.randint(0, self.grid_height - 1)
            
            # 检查是否与蛇身重叠
            if (grid_x, grid_y) not in snake_grid_positions:
                # 转换为像素坐标
                food_x = grid_x * self.cell_size
                food_y = grid_y * self.cell_size
                return (food_x, food_y)
                
        # 如果多次尝试后仍未找到有效位置，使用回退方法
        return self._generate_food_fallback(snake_grid_positions)
    
    def _generate_food_fallback(self, snake_grid_positions):
        """
        回退方法：当随机尝试多次失败时使用
        """
        # 收集所有可用位置
        available_positions = []
        for x in range(self.grid_width):
            for y in range(self.grid_height):
                if (x, y) not in snake_grid_positions:
                    available_positions.append((x, y))
        
        # 随机选择一个可用位置
        if available_positions:
            grid_x, grid_y = random.choice(available_positions)
            return (grid_x * self.cell_size, grid_y * self.cell_size)
        
        return None