import pygame
import math

class Player:
    def __init__(self, x, y, speed=5):
        self.x = x
        self.y = y
        self.speed = speed
        self.radius = 15
        self.direction = 'right'  # 初始方向向右
        self.next_direction = None  # 存储玩家下一次想要移动的方向
        self.mouth_open = True  # 控制嘴巴开合动画
        self.mouth_timer = 0
        
    def update(self, maze):
        # 尝试改变方向（如果玩家按了新的方向键）
        if self.next_direction:
            if self.can_move(self.next_direction, maze):
                self.direction = self.next_direction
                self.next_direction = None
        
        # 根据当前方向移动
        if self.direction == 'up':
            self.move(0, -self.speed, maze)
        elif self.direction == 'down':
            self.move(0, self.speed, maze)
        elif self.direction == 'left':
            self.move(-self.speed, 0, maze)
        elif self.direction == 'right':
            self.move(self.speed, 0, maze)
            
        # 更新嘴巴动画
        self.mouth_timer += 1
        if self.mouth_timer > 5:
            self.mouth_open = not self.mouth_open
            self.mouth_timer = 0
    
    def move(self, dx, dy, maze):
        new_x = self.x + dx
        new_y = self.y + dy
        
        # 检查碰撞
        if self.can_move(self.direction, maze):
            self.x = new_x
            self.y = new_y
    
    def can_move(self, direction, maze):
        # 计算玩家下一步的位置
        next_x, next_y = self.x, self.y
        
        if direction == 'up':
            next_y -= self.speed + self.radius
        elif direction == 'down':
            next_y += self.speed + self.radius
        elif direction == 'left':
            next_x -= self.speed + self.radius
        elif direction == 'right':
            next_x += self.speed + self.radius
            
        # 检查是否与墙壁碰撞
        cell_x = int(next_x // maze.cell_size)
        cell_y = int(next_y // maze.cell_size)
        
        # 确保在迷宫范围内
        if 0 <= cell_x < maze.width and 0 <= cell_y < maze.height:
            return maze.maze[cell_y][cell_x] != 1
        return False
    
    def draw(self, screen):
        # 绘制吃豆人
        color = (255, 255, 0)  # 黄色
        
        if self.mouth_open:
            # 张嘴状态
            if self.direction == 'right':
                start_angle = math.radians(45)
                end_angle = math.radians(315)
            elif self.direction == 'left':
                start_angle = math.radians(225)
                end_angle = math.radians(135)
            elif self.direction == 'up':
                start_angle = math.radians(315)
                end_angle = math.radians(225)
            elif self.direction == 'down':
                start_angle = math.radians(135)
                end_angle = math.radians(45)
            else:
                start_angle = 0
                end_angle = math.radians(360)
                
            pygame.draw.arc(screen, color, 
                          (self.x - self.radius, self.y - self.radius, 
                           self.radius * 2, self.radius * 2),
                          start_angle, end_angle, self.radius)
        else:
            # 闭嘴状态
            pygame.draw.circle(screen, color, (self.x, self.y), self.radius)