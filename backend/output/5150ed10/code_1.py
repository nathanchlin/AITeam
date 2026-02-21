import pygame
import math
from enum import Enum

class PlayerPlane:
    def __init__(self, x, y, screen_width, screen_height):
        """
        初始化玩家飞机
        
        参数:
            x, y: 初始位置坐标
            screen_width, screen_height: 屏幕尺寸，用于边界检测
        """
        self.x = x
        self.y = y
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # 飞机属性
        self.width = 40
        self.height = 50
        self.speed = 5
        self.max_speed = 8
        self.acceleration = 0.3
        self.deceleration = 0.2
        
        # 移动方向
        self.dx = 0
        self.dy = 0
        
        # 飞机状态
        self.is_alive = True
        self.invulnerable_time = 0  # 无敌时间
        
        # 射击相关
        self.can_shoot = True
        self.shoot_cooldown = 0
        self.shoot_delay = 10  # 射击冷却时间(帧数)
        
        # 飞机图像
        self.image = None
        self.create_image()
        
    def create_image(self):
        """创建玩家飞机的简单图形表示"""
        # 创建一个简单的三角形飞机
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        points = [
            (self.width // 2, 0),  # 顶部
            (0, self.height),     # 左下
            (self.width, self.height)  # 右下
        ]
        pygame.draw.polygon(self.image, (0, 200, 255), points)  # 亮蓝色飞机
        # 添加驾驶舱
        pygame.draw.circle(self.image, (0, 100, 200), (self.width // 2, self.height // 2), 5)
        
    def update(self, keys_pressed):
        """更新玩家飞机状态"""
        if not self.is_alive:
            return
            
        # 更新无敌时间
        if self.invulnerable_time > 0:
            self.invulnerable_time -= 1
            
        # 更新射击冷却
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        else:
            self.can_shoot = True
            
        # 处理输入
        self.handle_input(keys_pressed)
        
        # 更新位置
        self.x += self.dx
        self.y += self.dy
        
        # 边界检测
        self.check_boundaries()
        
    def handle_input(self, keys_pressed):
        """处理键盘输入"""
        # 重置速度
        target_dx = 0
        target_dy = 0
        
        # 检测方向键
        if keys_pressed[pygame.K_LEFT] or keys_pressed[pygame.K_a]:
            target_dx = -self.speed
        if keys_pressed[pygame.K_RIGHT] or keys_pressed[pygame.K_d]:
            target_dx = self.speed
        if keys_pressed[pygame.K_UP] or keys_pressed[pygame.K_w]:
            target_dy = -self.speed
        if keys_pressed[pygame.K_DOWN] or keys_pressed[pygame.K_s]:
            target_dy = self.speed
            
        # 对角线移动速度标准化
        if target_dx != 0 and target_dy != 0:
            factor = 0.7071  # 1/sqrt(2)
            target_dx *= factor
            target_dy *= factor
            
        # 平滑加速和减速
        if target_dx != 0:
            if self.dx * target_dx < 0:  # 方向相反
                self.dx *= (1 - self.deceleration)
            else:
                self.dx = self.dx + (target_dx - self.dx) * self.acceleration
                if abs(self.dx) > self.max_speed:
                    self.dx = self.max_speed if self.dx > 0 else -self.max_speed
        else:
            self.dx *= (1 - self.deceleration)
            
        if target_dy != 0:
            if self.dy * target_dy < 0:  # 方向相反
                self.dy *= (1 - self.deceleration)
            else:
                self.dy = self.dy + (target_dy - self.dy) * self.acceleration
                if abs(self.dy) > self.max_speed:
                    self.dy = self.max_speed if self.dy > 0 else -self.max_speed
        else:
            self.dy *= (1 - self.deceleration)
            
    def check_boundaries(self):
        """确保飞机不会飞出屏幕边界"""
        margin = 10  # 边界余量
        self.x = max(margin, min(self.screen_width - self.width - margin, self.x))
        self.y = max(margin, min(self.screen_height - self.height - margin, self.y))
        
    def shoot(self):
        """发射子弹"""
        if self.can_shoot and self.is_alive:
            self.can_shoot = False
            self.shoot_cooldown = self.shoot_delay
            # 返回子弹位置，供游戏主循环处理
            return Bullet(self.x + self.width // 2, self.y)
        return None
        
    def draw(self, screen):
        """绘制玩家飞机"""
        if self.is_alive:
            # 无敌期间闪烁效果
            if self.invulnerable_time > 0 and self.invulnerable_time % 10 < 5:
                screen.blit(self.image, (self.x, self.y))
            else:
                screen.blit(self.image, (self.x, self.y))
                
    def get_rect(self):
        """获取飞机的矩形碰撞区域"""
        return pygame.Rect(self.x, self.y, self.width, self.height)
        
    def take_damage(self):
        """受到伤害"""
        if self.invulnerable_time <= 0 and self.is_alive:
            self.is_alive = False
            # 可以在这里添加爆炸效果
            
    def respawn(self):
        """重生"""
        self.x = self.screen_width // 2 - self.width // 2
        self.y = self.screen_height - self.height - 20
        self.is_alive = True
        self.invulnerable_time = 120  # 2秒无敌时间(假设60FPS)