import math
import pygame

class BallPhysics:
    def __init__(self, x, y, radius, speed_x=0, speed_y=0):
        """
        初始化球体物理引擎
        
        参数:
            x, y: 球的初始位置
            radius: 球的半径
            speed_x, speed_y: 初始速度向量
        """
        self.x = x
        self.y = y
        self.radius = radius
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.gravity = 0  # 打砖块游戏通常不需要重力
        self.friction = 0.99  # 摩擦系数，模拟空气阻力
        self.bounce_damping = 0.95  # 反弹能量损失系数
        
    def update(self, dt):
        """
        更新球的位置和速度
        
        参数:
            dt: 时间增量(秒)
        """
        # 应用摩擦力
        self.speed_x *= self.friction
        self.speed_y *= self.friction
        
        # 更新位置
        self.x += self.speed_x * dt
        self.y += self.speed_y * dt
        
    def check_boundary_collision(self, width, height):
        """
        检查并处理与边界的碰撞
        
        参数:
            width, height: 边界尺寸
        """
        # 左右边界碰撞
        if self.x - self.radius <= 0:
            self.x = self.radius
            self.speed_x = -self.speed_x * self.bounce_damping
        elif self.x + self.radius >= width:
            self.x = width - self.radius
            self.speed_x = -self.speed_x * self.bounce_damping
            
        # 上下边界碰撞
        if self.y - self.radius <= 0:
            self.y = self.radius
            self.speed_y = -self.speed_y * self.bounce_damping
        elif self.y + self.radius >= height:
            self.y = height - self.radius
            self.speed_y = -self.speed_y * self.bounce_damping
            
    def check_paddle_collision(self, paddle):
        """
        检查并处理与挡板的碰撞
        
        参数:
            paddle: 挡板对象，需要有x, y, width, height属性
        """
        # 计算球与挡板中心的相对位置
        ball_center_x = self.x
        ball_center_y = self.y
        paddle_center_x = paddle.x + paddle.width / 2
        paddle_center_y = paddle.y + paddle.height / 2
        
        # 计算相对距离
        dx = ball_center_x - paddle_center_x
        dy = ball_center_y - paddle_center_y
        
        # 计算碰撞法线
        distance = math.sqrt(dx*dx + dy*dy)
        if distance == 0:  # 避免除以零
            nx, ny = 0, -1
        else:
            nx, ny = dx/distance, dy/distance
            
        # 检查是否发生碰撞
        # 简化版碰撞检测：检查球是否与挡矩形相交
        closest_x = max(paddle.x, min(ball_center_x, paddle.x + paddle.width))
        closest_y = max(paddle.y, min(ball_center_y, paddle.y + paddle.height))
        
        distance_x = ball_center_x - closest_x
        distance_y = ball_center_y - closest_y
        distance = math.sqrt(distance_x*distance_x + distance_y*distance_y)
        
        if distance < self.radius:
            # 碰撞发生，计算反弹
            overlap = self.radius - distance
            
            # 将球推出挡板
            self.x += nx * overlap
            self.y += ny * overlap
            
            # 计算反弹速度
            dot_product = self.speed_x * nx + self.speed_y * ny
            self.speed_x = (self.speed_x - 2 * dot_product * nx) * self.bounce_damping
            self.speed_y = (self.speed_y - 2 * dot_product * ny) * self.bounce_damping
            
            # 根据击中挡板的位置调整角度
            hit_pos = (ball_center_x - paddle.x) / paddle.width - 0.5  # -0.5 到 0.5
            angle_adjustment = hit_pos * math.pi / 3  # 最大调整60度
            speed = math.sqrt(self.speed_x**2 + self.speed_y**2)
            current_angle = math.atan2(self.speed_y, self.speed_x)
            new_angle = current_angle + angle_adjustment
            
            self.speed_x = speed * math.cos(new_angle)
            self.speed_y = speed * math.sin(new_angle)
            
            return True
        return False
        
    def check_brick_collision(self, brick):
        """
        检查并处理与砖块的碰撞
        
        参数:
            brick: 砖块对象，需要有x, y, width, height属性
        """
        # 计算球与砖块中心的相对位置
        ball_center_x = self.x
        ball_center_y = self.y
        brick_center_x = brick.x + brick.width / 2
        brick_center_y = brick.y + brick.height / 2
        
        # 计算相对距离
        dx = ball_center_x - brick_center_x
        dy = ball_center_y - brick_center_y
        
        # 计算碰撞法线
        distance = math.sqrt(dx*dx + dy*dy)
        if distance == 0:  # 避免除以零
            nx, ny = 1, 0
        else:
            nx, ny = dx/distance, dy/distance
            
        # 检查是否发生碰撞
        closest_x = max(brick.x, min(ball_center_x, brick.x + brick.width))
        closest_y = max(brick.y, min(ball_center_y, brick.y + brick.height))
        
        distance_x = ball_center_x - closest_x
        distance_y = ball_center_y - closest_y
        distance = math.sqrt(distance_x*distance_x + distance_y*distance_y)
        
        if distance < self.radius:
            # 碰撞发生，计算反弹
            overlap = self.radius - distance
            
            # 将球推出砖块
            self.x += nx * overlap
            self.y += ny * overlap
            
            # 计算反弹速度
            dot_product = self.speed_x * nx + self.speed_y * ny
            self.speed_x = (self.speed_x - 2 * dot_product * nx) * self.bounce_damping
            self.speed_y = (self.speed_y - 2 * dot_product * ny) * self.bounce_damping
            
            return True
        return False
        
    def draw(self, screen):
        """
        绘制球体
        
        参数:
            screen: Pygame屏幕对象
        """
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), self.radius)