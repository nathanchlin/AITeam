import math
import pygame

class Tank:
    def __init__(self, x, y, angle=0, color=(0, 128, 0), speed=2, rotation_speed=2):
        """
        初始化坦克
        
        参数:
            x, y: 坦克的初始位置
            angle: 坦克的初始角度(度)
            color: 坦克的RGB颜色
            speed: 坦克的移动速度
            rotation_speed: 坦克的旋转速度(度/帧)
        """
        self.x = x
        self.y = y
        self.angle = angle  # 坦克主体角度
        self.turret_angle = angle  # 炮塔角度
        self.color = color
        self.speed = speed
        self.rotation_speed = rotation_speed
        self.width = 40
        self.height = 30
        self.turret_length = 25
        self.turret_width = 8
        self.health = 100
        self.ammo = 50
        self.last_shot_time = 0
        self.shot_cooldown = 500  # 射击冷却时间(毫秒)
        
    def move(self, direction):
        """
        移动坦克
        
        参数:
            direction: 'forward' 或 'backward'
        """
        rad = math.radians(self.angle)
        if direction == 'forward':
            self.x += self.speed * math.cos(rad)
            self.y -= self.speed * math.sin(rad)  # Pygame坐标系中y轴向下为正
        elif direction == 'backward':
            self.x -= self.speed * math.cos(rad)
            self.y += self.speed * math.sin(rad)
    
    def rotate(self, direction):
        """
        旋转坦克
        
        参数:
            direction: 'left' 或 'right'
        """
        if direction == 'left':
            self.angle -= self.rotation_speed
        elif direction == 'right':
            self.angle += self.rotation_speed
        
        # 确保角度在0-360度之间
        self.angle %= 360
    
    def rotate_turret(self, direction):
        """
        旋转炮塔
        
        参数:
            direction: 'left' 或 'right'
        """
        if direction == 'left':
            self.turret_angle -= self.rotation_speed * 1.5
        elif direction == 'right':
            self.turret_angle += self.rotation_speed * 1.5
        
        # 确保角度在0-360度之间
        self.turret_angle %= 360
    
    def can_shoot(self, current_time):
        """检查是否可以射击"""
        return current_time - self.last_shot_time > self.shot_cooldown and self.ammo > 0
    
    def shoot(self, current_time):
        """射击"""
        if self.can_shoot(current_time):
            self.last_shot_time = current_time
            self.ammo -= 1
            
            # 计算子弹初始位置(炮塔末端)
            rad = math.radians(self.turret_angle)
            bullet_x = self.x + self.turret_length * math.cos(rad)
            bullet_y = self.y - self.turret_length * math.sin(rad)
            
            # 创建并返回子弹
            return Bullet(bullet_x, bullet_y, self.turret_angle, self.color)
        return None
    
    def get_rect(self):
        """获取坦克的矩形碰撞区域"""
        return pygame.Rect(self.x - self.width//2, self.y - self.height//2, 
                          self.width, self.height)
    
    def draw(self, screen):
        """绘制坦克"""
        # 绘制坦克主体
        tank_points = self._get_tank_points()
        pygame.draw.polygon(screen, self.color, tank_points)
        
        # 绘制炮塔
        turret_end_x = self.x + self.turret_length * math.cos(math.radians(self.turret_angle))
        turret_end_y = self.y - self.turret_length * math.sin(math.radians(self.turret_angle))
        pygame.draw.line(screen, self.color, (self.x, self.y), 
                        (turret_end_x, turret_end_y), self.turret_width)
    
    def _get_tank_points(self):
        """获取坦克多边形顶点"""
        # 计算坦克四个角的坐标
        rad = math.radians(self.angle)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        
        # 坦克的四个角(相对于中心)
        half_width = self.width / 2
        half_height = self.height / 2
        
        points = [
            (-half_width, -half_height),
            (half_width, -half_height),
            (half_width, half_height),
            (-half_width, half_height)
        ]
        
        # 旋转并平移到正确位置
        rotated_points = []
        for px, py in points:
            rx = px * cos_a - py * sin_a + self.x
            ry = px * sin_a + py * cos_a + self.y
            rotated_points.append((rx, ry))
        
        return rotated_points