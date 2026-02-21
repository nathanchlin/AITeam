import pygame
import math

class Bird:
    def __init__(self, x, y, size=30):
        """
        初始化小鸟角色
        :param x: 初始x坐标
        :param y: 初始y坐标
        :param size: 小鸟大小
        """
        self.x = x
        self.y = y
        self.size = size
        self.velocity = 0  # 垂直速度
        self.gravity = 0.5  # 重力加速度
        self.jump_strength = -8  # 跳跃力度
        self.rotation = 0  # 旋转角度
        self.max_rotation = 25  # 最大旋转角度
        self.min_rotation = -90  # 最小旋转角度
        self.rotation_speed = 3  # 旋转速度
        self.color = (255, 255, 0)  # 小鸟颜色（黄色）
        self.wing_positions = [0, 5, 10]  # 翅膀动画位置
        self.current_wing_pos = 0
        self.wing_animation_speed = 5  # 翅膀动画速度
        self.wing_counter = 0
        
    def jump(self):
        """使小鸟跳跃"""
        self.velocity = self.jump_strength
        
    def update(self):
        """更新小鸟状态"""
        # 应用重力
        self.velocity += self.gravity
        self.y += self.velocity
        
        # 更新旋转角度
        if self.velocity < 0:  # 上升时
            self.rotation = max(self.rotation - self.rotation_speed, self.min_rotation)
        else:  # 下降时
            self.rotation = min(self.rotation + self.rotation_speed, self.max_rotation)
            
        # 更新翅膀动画
        self.wing_counter += 1
        if self.wing_counter >= self.wing_animation_speed:
            self.wing_counter = 0
            self.current_wing_pos = (self.current_wing_pos + 1) % len(self.wing_positions)
            
    def draw(self, screen):
        """绘制小鸟"""
        # 保存当前状态
        bird_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        
        # 绘制小鸟身体
        pygame.draw.circle(bird_surface, self.color, (self.size, self.size), self.size)
        
        # 绘制小鸟眼睛
        eye_offset_x = self.size // 2
        eye_offset_y = -self.size // 3
        pygame.draw.circle(bird_surface, (255, 255, 255), 
                         (self.size + eye_offset_x, self.size + eye_offset_y), self.size // 4)
        pygame.draw.circle(bird_surface, (0, 0, 0), 
                         (self.size + eye_offset_x, self.size + eye_offset_y), self.size // 8)
        
        # 绘制小鸟嘴巴
        beak_points = [
            (self.size + self.size, self.size),
            (self.size + self.size + self.size // 2, self.size - self.size // 6),
            (self.size + self.size + self.size // 2, self.size + self.size // 6)
        ]
        pygame.draw.polygon(bird_surface, (255, 165, 0), beak_points)
        
        # 绘制翅膀（带动画效果）
        wing_offset = self.wing_positions[self.current_wing_pos]
        wing_points = [
            (self.size - self.size // 2, self.size),
            (self.size - self.size, self.size - self.size // 3 + wing_offset),
            (self.size - self.size // 2, self.size - self.size // 2 + wing_offset)
        ]
        pygame.draw.polygon(bird_surface, (255, 200, 0), wing_points)
        
        # 绘制尾巴
        tail_points = [
            (self.size - self.size, self.size),
            (self.size - self.size * 1.5, self.size - self.size // 4),
            (self.size - self.size * 1.5, self.size + self.size // 4)
        ]
        pygame.draw.polygon(bird_surface, (255, 180, 0), tail_points)
        
        # 旋转小鸟
        rotated_bird = pygame.transform.rotate(bird_surface, self.rotation)
        bird_rect = rotated_bird.get_rect(center=(self.x, self.y))
        
        # 绘制到屏幕
        screen.blit(rotated_bird, bird_rect)
        
    def get_rect(self):
        """获取小鸟的碰撞矩形"""
        return pygame.Rect(self.x - self.size, self.y - self.size, self.size * 2, self.size * 2)