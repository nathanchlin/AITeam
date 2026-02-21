import pygame
import math
import random

class Asteroid:
    def __init__(self, x, y, size, speed=None, direction=None):
        """
        初始化陨石
        :param x: 初始x坐标
        :param y: 初始y坐标
        :param size: 陨石大小 (1=小, 2=中, 3=大)
        :param speed: 可选，指定速度向量
        :param direction: 可选，指定移动方向(角度)
        """
        self.x = x
        self.y = y
        self.size = size  # 1=小, 2=中, 3=大
        
        # 根据大小设置属性
        self.radius = {1: 15, 2: 25, 3: 40}[size]
        self.health = size
        self.points = {1: 100, 2: 50, 3: 20}[size]
        
        # 如果没有提供速度，则随机生成
        if speed is None:
            speed = random.uniform(1, 3) * (4 - size)  # 小陨石更快
        self.speed = speed
        
        # 如果没有提供方向，则随机生成
        if direction is None:
            direction = random.uniform(0, 2 * math.pi)
        self.dx = math.cos(direction) * speed
        self.dy = math.sin(direction) * speed
        
        # 旋转属性
        self.rotation = random.uniform(0, 2 * math.pi)
        self.rotation_speed = random.uniform(-0.05, 0.05)
        
        # 生成不规则形状
        self.generate_shape()
        
        # 颜色根据大小变化
        self.color = {1: (200, 200, 200), 2: (150, 150, 150), 3: (100, 100, 100)}[size]
    
    def generate_shape(self):
        """生成不规则形状的点"""
        self.points_list = []
        num_points = random.randint(8, 12)
        
        for i in range(num_points):
            angle = (2 * math.pi * i) / num_points
            # 添加一些随机变化使形状不规则
            radius_variation = random.uniform(0.8, 1.2)
            r = self.radius * radius_variation
            x = r * math.cos(angle)
            y = r * math.sin(angle)
            self.points_list.append((x, y))
    
    def update(self):
        """更新陨石位置和旋转"""
        self.x += self.dx
        self.y += self.dy
        self.rotation += self.rotation_speed
    
    def draw(self, screen):
        """绘制陨石"""
        # 计算旋转后的点
        rotated_points = []
        for px, py in self.points_list:
            # 旋转变换
            rotated_x = px * math.cos(self.rotation) - py * math.sin(self.rotation)
            rotated_y = px * math.sin(self.rotation) + py * math.cos(self.rotation)
            # 平移到陨石位置
            rotated_points.append((self.x + rotated_x, self.y + rotated_y))
        
        pygame.draw.polygon(screen, self.color, rotated_points)
    
    def get_rect(self):
        """获取用于碰撞检测的矩形"""
        return pygame.Rect(self.x - self.radius, self.y - self.radius, 
                          self.radius * 2, self.radius * 2)
    
    def split(self):
        """分裂陨石（大陨石被击中时）"""
        if self.size == 1:
            return []  # 小陨石不再分裂
        
        new_size = self.size - 1
        new_asteroids = []
        
        # 创建2个新陨石
        for _ in range(2):
            # 随机偏移位置
            offset_x = random.uniform(-10, 10)
            offset_y = random.uniform(-10, 10)
            # 稍微增加速度
            new_speed = self.speed * random.uniform(1.1, 1.3)
            # 随机新方向
            new_direction = random.uniform(0, 2 * math.pi)
            
            new_asteroid = Asteroid(
                self.x + offset_x, 
                self.y + offset_y, 
                new_size, 
                new_speed, 
                new_direction
            )
            new_asteroids.append(new_asteroid)
        
        return new_asteroids