import random
import pygame
from enum import Enum

class Difficulty(Enum):
    EASY = 1
    MEDIUM = 2
    HARD = 3
    EXTREME = 4

class Obstacle:
    def __init__(self, x, y, width, height, speed, obstacle_type):
        self.rect = pygame.Rect(x, y, width, height)
        self.speed = speed
        self.type = obstacle_type
        self.color = self._get_color_by_type()
    
    def _get_color_by_type(self):
        colors = {
            'normal': (255, 0, 0),
            'fast': (255, 165, 0),
            'big': (139, 0, 0),
            'moving': (255, 20, 147)
        }
        return colors.get(self.type, (255, 0, 0))
    
    def update(self):
        self.rect.x -= self.speed
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

class ObstacleGenerator:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.obstacles = []
        self.last_obstacle_time = 0
        self.difficulty = Difficulty.EASY
        self.game_time = 0
        
    def update_difficulty(self, game_time):
        # 随着游戏时间增加难度
        if game_time < 20:
            self.difficulty = Difficulty.EASY
        elif game_time < 40:
            self.difficulty = Difficulty.MEDIUM
        elif game_time < 70:
            self.difficulty = Difficulty.HARD
        else:
            self.difficulty = Difficulty.EXTREME
    
    def get_spawn_interval(self):
        intervals = {
            Difficulty.EASY: 1500,  # 1.5秒
            Difficulty.MEDIUM: 1000,  # 1秒
            Difficulty.HARD: 700,    # 0.7秒
            Difficulty.EXTREME: 400   # 0.4秒
        }
        return intervals[self.difficulty]
    
    def get_obstacle_speed(self):
        speeds = {
            Difficulty.EASY: 5,
            Difficulty.MEDIUM: 7,
            Difficulty.HARD: 10,
            Difficulty.EXTREME: 15
        }
        return speeds[self.difficulty]
    
    def generate_obstacle(self, current_time):
        if current_time - self.last_obstacle_time > self.get_spawn_interval():
            obstacle_types = ['normal', 'fast', 'big', 'moving']
            weights = [0.5, 0.3, 0.15, 0.05]  # 不同类型障碍物的生成概率
            
            obstacle_type = random.choices(obstacle_types, weights=weights)[0]
            
            # 根据类型设置障碍物属性
            if obstacle_type == 'normal':
                width = random.randint(30, 60)
                height = random.randint(50, 150)
                speed = self.get_obstacle_speed()
            elif obstacle_type == 'fast':
                width = random.randint(20, 40)
                height = random.randint(40, 100)
                speed = self.get_obstacle_speed() * 1.5
            elif obstacle_type == 'big':
                width = random.randint(60, 100)
                height = random.randint(100, 200)
                speed = self.get_obstacle_speed() * 0.7
            else:  # moving
                width = random.randint(40, 70)
                height = random.randint(60, 120)
                speed = self.get_obstacle_speed()
            
            y = random.randint(0, self.screen_height - height)
            obstacle = Obstacle(self.screen_width, y, width, height, speed, obstacle_type)
            
            # 为moving类型障碍物添加垂直移动特性
            if obstacle_type == 'moving':
                obstacle.moving_up = random.choice([True, False])
                obstacle.vertical_speed = random.uniform(2, 5)
            
            self.obstacles.append(obstacle)
            self.last_obstacle_time = current_time
    
    def update_obstacles(self, current_time):
        # 更新难度
        self.update_difficulty(current_time // 1000)  # 转换为秒
        
        # 生成新障碍物
        self.generate_obstacle(current_time)
        
        # 更新现有障碍物
        for obstacle in self.obstacles[:]:
            obstacle.update()
            
            # 处理moving类型障碍物的垂直移动
            if hasattr(obstacle, 'moving_up'):
                if obstacle.moving_up:
                    obstacle.rect.y -= obstacle.vertical_speed
                    if obstacle.rect.y <= 0:
                        obstacle.moving_up = False
                else:
                    obstacle.rect.y += obstacle.vertical_speed
                    if obstacle.rect.y >= self.screen_height - obstacle.rect.height:
                        obstacle.moving_up = True
            
            # 移除屏幕外的障碍物
            if obstacle.rect.right < 0:
                self.obstacles.remove(obstacle)
    
    def draw_obstacles(self, screen):
        for obstacle in self.obstacles:
            obstacle.draw(screen)