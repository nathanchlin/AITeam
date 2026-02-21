import pygame
import math
from enum import Enum

class WeaponType(Enum):
    BASIC = 1
    SPREAD = 2
    LASER = 3

class PlayerAircraft:
    def __init__(self, x, y, screen_width, screen_height):
        self.x = x
        self.y = y
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.width = 50
        self.height = 50
        self.speed = 5
        self.rotation = 0  # 角度，0表示向上
        self.health = 100
        self.max_health = 100
        self.weapon_type = WeaponType.BASIC
        self.shoot_cooldown = 0
        self.shoot_delay = 10  # 射击冷却时间（帧数）
        self.is_alive = True
        
        # 加载飞机图像
        self.image = self.load_aircraft_image()
        self.original_image = self.image
        
        # 动画相关
        self.animation_frame = 0
        self.animation_speed = 0.2
        self.is_shooting = False
        
    def load_aircraft_image(self):
        """加载飞机图像，如果没有则创建一个简单的三角形"""
        try:
            # 这里应该加载实际的飞机图像
            # image = pygame.image.load("player_aircraft.png").convert_alpha()
            # return pygame.transform.scale(image, (self.width, self.height))
            
            # 临时创建一个简单的三角形作为飞机
            image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            points = [(25, 0), (0, 50), (50, 50)]
            pygame.draw.polygon(image, (0, 150, 255), points)
            return image
        except:
            # 如果加载失败，创建一个简单的矩形
            image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.rect(image, (0, 150, 255), (0, 0, self.width, self.height))
            return image
    
    def update(self, keys):
        """更新飞机状态"""
        if not self.is_alive:
            return
            
        # 移动控制
        dx, dy = 0, 0
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = self.speed
            
        # 更新位置
        self.x += dx
        self.y += dy
        
        # 边界检查
        self.x = max(0, min(self.screen_width - self.width, self.x))
        self.y = max(0, min(self.screen_height - self.height, self.y))
        
        # 旋转控制（跟随鼠标）
        mouse_x, mouse_y = pygame.mouse.get_pos()
        dx = mouse_x - (self.x + self.width // 2)
        dy = mouse_y - (self.y + self.height // 2)
        self.rotation = math.degrees(math.atan2(dx, -dy))
        
        # 更新图像旋转
        self.image = pygame.transform.rotate(self.original_image, -self.rotation)
        
        # 射击控制
        if keys[pygame.K_SPACE] and self.shoot_cooldown <= 0:
            self.is_shooting = True
            self.shoot_cooldown = self.shoot_delay
            return self.shoot()
        else:
            self.is_shooting = False
            
        # 更新射击冷却
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
            
        # 更新动画
        self.animation_frame += self.animation_speed
        
        return None
    
    def shoot(self):
        """发射子弹，根据武器类型返回不同的子弹"""
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2
        
        # 计算子弹发射方向（飞机朝向）
        rad = math.radians(self.rotation)
        dx = math.sin(rad)
        dy = -math.cos(rad)
        
        if self.weapon_type == WeaponType.BASIC:
            return [Bullet(center_x, center_y, dx, dy)]
        elif self.weapon_type == WeaponType.SPREAD:
            # 扇形射击
            bullets = []
            for angle_offset in [-15, 0, 15]:
                rad_offset = math.radians(self.rotation + angle_offset)
                dx_offset = math.sin(rad_offset)
                dy_offset = -math.cos(rad_offset)
                bullets.append(Bullet(center_x, center_y, dx_offset, dy_offset))
            return bullets
        elif self.weapon_type == WeaponType.LASER:
            # 激光，速度更快
            return [Bullet(center_x, center_y, dx, dy, is_laser=True)]
            
    def draw(self, screen):
        """绘制飞机"""
        if not self.is_alive:
            return
            
        # 绘制飞机
        rect = self.image.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
        screen.blit(self.image, rect)
        
        # 绘制射击效果
        if self.is_shooting:
            self.draw_muzzle_flash(screen, rect.center)
            
        # 绘制血条
        self.draw_health_bar(screen)
        
    def draw_muzzle_flash(self, screen, center):
        """绘制枪口火焰效果"""
        rad = math.radians(self.rotation)
        flash_x = center[0] - math.sin(rad) * 30
        flash_y = center[1] + math.cos(rad) * 30
        
        # 简单的火焰效果
        pygame.draw.circle(screen, (255, 200, 0), (int(flash_x), int(flash_y)), 5)
        pygame.draw.circle(screen, (255, 100, 0), (int(flash_x), int(flash_y)), 3)
        
    def draw_health_bar(self, screen):
        """绘制血条"""
        bar_width = 50
        bar_height = 6
        bar_x = self.x + self.width // 2 - bar_width // 2
        bar_y = self.y - 15
        
        # 背景
        pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        
        # 当前血量
        current_width = int(bar_width * (self.health / self.max_health))
        pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, current_width, bar_height))
        
    def take_damage(self, damage):
        """受到伤害"""
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.is_alive = False
            
    def change_weapon(self, weapon_type):
        """切换武器类型"""
        self.weapon_type = weapon_type
        
    def respawn(self, x, y):
        """重生"""
        self.x = x
        self.y = y
        self.health = self.max_health
        self.is_alive = True