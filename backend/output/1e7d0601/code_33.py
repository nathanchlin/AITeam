import pygame
from enum import Enum
from typing import List, Tuple

class BulletType(Enum):
    PLAYER_NORMAL = 1
    PLAYER_DOUBLE = 2
    PLAYER_SPREAD = 3
    ENEMY_NORMAL = 4
    ENEMY_FAST = 5
    ENEMY_HEAVY = 6

class Bullet:
    def __init__(self, x: float, y: float, bullet_type: BulletType, damage: int = 1, 
                 speed: float = 5.0, direction: Tuple[float, float] = (0, -1),
                 color: Tuple[int, int, int] = (255, 255, 0), size: int = 5):
        self.x = x
        self.y = y
        self.bullet_type = bullet_type
        self.damage = damage
        self.speed = speed
        self.direction = direction  # (dx, dy) 归一化向量
        self.color = color
        self.size = size
        self.active = True
        self.trail = []  # 用于轨迹效果
        self.max_trail_length = 10
        
    def update(self):
        """更新子弹位置"""
        self.x += self.direction[0] * self.speed
        self.y += self.direction[1] * self.speed
        
        # 添加轨迹点
        self.trail.append((self.x, self.y))
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)
        
        # 检查是否超出屏幕
        if (self.x < -50 or self.x > pygame.display.get_surface().get_width() + 50 or
            self.y < -50 or self.y > pygame.display.get_surface().get_height() + 50):
            self.active = False
    
    def draw(self, screen):
        """绘制子弹和轨迹"""
        # 绘制轨迹
        for i, pos in enumerate(self.trail):
            alpha = int(255 * (i / len(self.trail)))
            trail_color = (*self.color, alpha)
            trail_size = int(self.size * (i / len(self.trail)))
            if trail_size > 0:
                pygame.draw.circle(screen, trail_color[:3], (int(pos[0]), int(pos[1])), trail_size)
        
        # 绘制子弹主体
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)
        
        # 添加发光效果
        glow_size = self.size + 2
        glow_color = tuple(min(255, c + 50) for c in self.color)
        pygame.draw.circle(screen, glow_color, (int(self.x), int(self.y)), glow_size, 1)
    
    def get_rect(self):
        """获取子弹的碰撞矩形"""
        return pygame.Rect(self.x - self.size, self.y - self.size, self.size * 2, self.size * 2)