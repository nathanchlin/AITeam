import pygame
import math
import random

class PlayerShip:
    def __init__(self, x, y, game_width, game_height):
        self.x = x
        self.y = y
        self.angle = 0  # 角度，0表示向上
        self.velocity_x = 0
        self.velocity_y = 0
        self.acceleration = 0.5
        self.max_speed = 8
        self.rotation_speed = 5
        self.friction = 0.98
        self.radius = 15  # 碰撞半径
        
        # 游戏区域尺寸
        self.game_width = game_width
        self.game_height = game_height
        
        # 控制状态
        self.keys_pressed = set()
        self.touch_controls = {
            'left': False,
            'right': False,
            'up': False,
            'fire': False
        }
        
        # 射击相关
        self.can_shoot = True
        self.shoot_cooldown = 250  # 毫秒
        self.last_shot_time = 0
        
        # 生命值
        self.health = 100
        self.max_health = 100
        
    def update(self, current_time):
        # 处理旋转
        if 'left' in self.keys_pressed or self.touch_controls['left']:
            self.angle -= self.rotation_speed
        if 'right' in self.keys_pressed or self.touch_controls['right']:
            self.angle += self.rotation_speed
            
        # 处理推进
        if 'up' in self.keys_pressed or self.touch_controls['up']:
            # 将角度转换为弧度
            rad_angle = math.radians(self.angle - 90)  # -90因为0度是向上
            self.velocity_x += math.cos(rad_angle) * self.acceleration
            self.velocity_y += math.sin(rad_angle) * self.acceleration
            
        # 应用摩擦力
        self.velocity_x *= self.friction
        self.velocity_y *= self.friction
        
        # 限制最大速度
        speed = math.sqrt(self.velocity_x**2 + self.velocity_y**2)
        if speed > self.max_speed:
            self.velocity_x = (self.velocity_x / speed) * self.max_speed
            self.velocity_y = (self.velocity_y / speed) * self.max_speed
            
        # 更新位置
        self.x += self.velocity_x
        self.y += self.velocity_y
        
        # 屏幕边界处理（环绕）
        self.x = self.x % self.game_width
        self.y = self.y % self.game_height
        
        # 射击冷却
        if current_time - self.last_shot_time > self.shoot_cooldown:
            self.can_shoot = True
            
    def shoot(self, current_time):
        if self.can_shoot:
            self.can_shoot = False
            self.last_shot_time = current_time
            # 创建子弹，从飞船前端发射
            rad_angle = math.radians(self.angle - 90)
            bullet_x = self.x + math.cos(rad_angle) * (self.radius + 5)
            bullet_y = self.y + math.sin(rad_angle) * (self.radius + 5)
            bullet_vx = math.cos(rad_angle) * 15 + self.velocity_x
            bullet_vy = math.sin(rad_angle) * 15 + self.velocity_y
            return Bullet(bullet_x, bullet_y, bullet_vx, bullet_vy)
        return None
        
    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0
            
    def draw(self, screen):
        # 绘制飞船主体
        points = []
        # 飞船的三个顶点
        ship_points = [
            (0, -self.radius),      # 顶点
            (-self.radius * 0.8, self.radius),  # 左下
            (self.radius * 0.8, self.radius)    # 右下
        ]
        
        # 旋转并平移点
        for px, py in ship_points:
            # 旋转
            rad_angle = math.radians(self.angle)
            rotated_x = px * math.cos(rad_angle) - py * math.sin(rad_angle)
            rotated_y = px * math.sin(rad_angle) + py * math.cos(rad_angle)
            # 平移
            points.append((self.x + rotated_x, self.y + rotated_y))
            
        pygame.draw.polygon(screen, (0, 255, 0), points)
        
        # 绘制推进器火焰（当加速时）
        if 'up' in self.keys_pressed or self.touch_controls['up']:
            flame_points = []
            flame_base_points = [
                (-self.radius * 0.4, self.radius),
                (0, self.radius + random.randint(5, 15)),
                (self.radius * 0.4, self.radius)
            ]
            
            for px, py in flame_base_points:
                # 旋转
                rad_angle = math.radians(self.angle)
                rotated_x = px * math.cos(rad_angle) - py * math.sin(rad_angle)
                rotated_y = px * math.sin(rad_angle) + py * math.cos(rad_angle)
                # 平移
                flame_points.append((self.x + rotated_x, self.y + rotated_y))
                
            pygame.draw.polygon(screen, (255, 165, 0), flame_points)
            
        # 绘制生命条
        bar_width = 40
        bar_height = 6
        bar_x = self.x - bar_width // 2
        bar_y = self.y - self.radius - 15
        
        # 背景
        pygame.draw.rect(screen, (100, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        # 当前生命值
        health_width = int(bar_width * (self.health / self.max_health))
        pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, health_width, bar_height))