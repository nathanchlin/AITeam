from enum import Enum
from collections import deque
import random

class Direction(Enum):
    """蛇的移动方向枚举"""
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    
    def opposite(self):
        """返回相反方向"""
        opposites = {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT
        }
        return opposites[self]

class GameState:
    """游戏状态管理类"""
    
    def __init__(self, width=20, height=20):
        self.width = width
        self.height = height
        self.reset()
    
    def reset(self):
        """重置游戏状态"""
        # 初始化蛇的位置（从中间开始）
        center_x = self.width // 2
        center_y = self.height // 2
        self.snake = deque([(center_x, center_y), (center_x-1, center_y), (center_x-2, center_y)])
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT
        self.score = 0
        self.game_over = False
        self.food = self._generate_food()
        self.speed = 200  # 毫秒
    
    def _generate_food(self):
        """生成食物位置，确保不在蛇身上"""
        while True:
            food = (
                random.randint(0, self.width - 1),
                random.randint(0, self.height - 1)
            )
            if food not in self.snake:
                return food
    
    def change_direction(self, new_direction):
        """改变蛇的移动方向，防止180度转向"""
        if new_direction != self.direction.opposite():
            self.next_direction = new_direction
    
    def update(self):
        """更新游戏状态"""
        if self.game_over:
            return
        
        # 更新方向
        self.direction = self.next_direction
        
        # 计算新的头部位置
        head_x, head_y = self.snake[0]
        dx, dy = self.direction.value
        new_head = (head_x + dx, head_y + dy)
        
        # 检查是否撞墙
        if (new_head[0] < 0 or new_head[0] >= self.width or 
            new_head[1] < 0 or new_head[1] >= self.height):
            self.game_over = True
            return
        
        # 检查是否撞到自己
        if new_head in self.snake:
            self.game_over = True
            return
        
        # 移动蛇
        self.snake.appendleft(new_head)
        
        # 检查是否吃到食物
        if new_head == self.food:
            self.score += 1
            self.food = self._generate_food()
            # 每得5分增加速度
            if self.score % 5 == 0:
                self.speed = max(50, self.speed - 20)
        else:
            self.snake.pop()
    
    def get_grid(self):
        """获取当前游戏网格状态，用于渲染"""
        grid = [[0 for _ in range(self.width)] for _ in range(self.height)]
        
        # 标记蛇身
        for i, (x, y) in enumerate(self.snake):
            if i == 0:  # 蛇头
                grid[y][x] = 2
            else:  # 蛇身
                grid[y][x] = 1
        
        # 标记食物
        food_x, food_y = self.food
        grid[food_y][food_x] = 3
        
        return grid