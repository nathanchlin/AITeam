import math
import pygame

class PhysicsEngine:
    def __init__(self, gravity=9.8, air_resistance=0.01):
        """
        初始化物理引擎
        :param gravity: 重力加速度 (像素/秒²)
        :param air_resistance: 空气阻力系数
        """
        self.gravity = gravity
        self.air_resistance = air_resistance
        self.objects = []
        
    def add_object(self, obj):
        """添加物理对象到引擎"""
        self.objects.append(obj)
        
    def update(self, dt):
        """更新所有物理对象"""
        for obj in self.objects:
            self.apply_gravity(obj, dt)
            self.apply_air_resistance(obj, dt)
            obj.update_position(dt)
            
    def apply_gravity(self, obj, dt):
        """应用重力"""
        obj.velocity_y += self.gravity * dt
        
    def apply_air_resistance(self, obj, dt):
        """应用空气阻力"""
        speed = math.sqrt(obj.velocity_x**2 + obj.velocity_y**2)
        if speed > 0:
            drag_force = self.air_resistance * speed
            obj.velocity_x -= (obj.velocity_x / speed) * drag_force * dt
            obj.velocity_y -= (obj.velocity_y / speed) * drag_force * dt
            
    def check_collisions(self):
        """检测所有对象之间的碰撞"""
        for i in range(len(self.objects)):
            for j in range(i + 1, len(self.objects)):
                if self.check_collision(self.objects[i], self.objects[j]):
                    self.resolve_collision(self.objects[i], self.objects[j])
                    
    def check_collision(self, obj1, obj2):
        """检测两个对象是否碰撞"""
        distance = math.sqrt((obj1.x - obj2.x)**2 + (obj1.y - obj2.y)**2)
        return distance < (obj1.radius + obj2.radius)
        
    def resolve_collision(self, obj1, obj2):
        """处理碰撞后的物理反应"""
        # 计算碰撞法线
        dx = obj2.x - obj1.x
        dy = obj2.y - obj1.y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance == 0:  # 防止除以零
            distance = 0.01
            
        # 单位法线向量
        nx = dx / distance
        ny = dy / distance
        
        # 相对速度
        dvx = obj1.velocity_x - obj2.velocity_x
        dvy = obj1.velocity_y - obj2.velocity_y
        
        # 相对速度在法线方向的分量
        dvn = dvx * nx + dvy * ny
        
        # 如果物体正在分离，不处理碰撞
        if dvn > 0:
            return
            
        # 计算冲量
        restitution = 0.6  # 恢复系数 (弹性)
        impulse = 2 * dvn / (1/obj1.mass + 1/obj2.mass)
        
        # 应用冲量
        obj1.velocity_x -= impulse * nx / obj1.mass * restitution
        obj1.velocity_y -= impulse * ny / obj1.mass * restitution
        obj2.velocity_x += impulse * nx / obj2.mass * restitution
        obj2.velocity_y += impulse * ny / obj2.mass * restitution
        
        # 分离重叠的物体
        overlap = (obj1.radius + obj2.radius) - distance
        separate_x = nx * overlap / 2
        separate_y = ny * overlap / 2
        obj1.x -= separate_x
        obj1.y -= separate_y
        obj2.x += separate_x
        obj2.y += separate_y