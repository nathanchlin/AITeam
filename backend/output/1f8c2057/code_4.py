class ConsoleRenderer(Renderer):
    def __init__(self, config: GameConfig):
        self.config = config
        
    def render(self, state: GameState):
        self.clear()
        
        # 创建网格
        grid = [[' ' for _ in range(self.config.grid_width)] 
                for _ in range(self.config.grid_height)]
        
        # 渲染蛇
        for i, segment in enumerate(state.snake.body):
            if i == 0:
                grid[segment.y][segment.x] = 'O'  # 蛇头
            else:
                grid[segment.y][segment.x] = 'o'  # 蛇身
        
        # 渲染食物
        for food in state.food:
            if food.type == "normal":
                grid[food.position.y][food.position.x] = '*'
            else:
                grid[food.position.y][food.position.x] = '$'  # 特殊食物
        
        # 打印网格
        print('+' + '-' * self.config.grid_width + '+')
        for row in grid:
            print('|' + ''.join(row) + '|')
        print('+' + '-' * self.config.grid_width + '+')
        
        # 打印分数
        print(f"Score: {state.score} | Level: {state.level}")
        
        if state.is_game_over:
            print("Game Over!")
        elif state.is_paused:
            print("Paused - Press any key to continue")
    
    def clear(self):
        import os
        os.system('cls' if os.name == 'nt' else 'clear')