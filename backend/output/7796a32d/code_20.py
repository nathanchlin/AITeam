import random
import math
from enum import Enum

class PlatformType(Enum):
    NORMAL = "normal"      # 普通平台
    MOVING = "moving"      # 左右移动平台
    BREAKING = "breaking"  # 会断裂的平台
    SPRING = "spring"      # 弹跳平台

class ObstacleType(Enum):
    SPIKE = "spike"        # 尖刺
    MOVING_SPIKE = "moving_spike"  # 移动尖刺
    WIND = "wind"          # 风力区域

class Platform:
    def __init__(self, x, y, width, platform_type=PlatformType.NORMAL, 
                 moving_speed=0, moving_range=0, break_timer=0):
        self.x = x
        self.y = y
        self.width = width
        self.type = platform_type
        self.moving_speed = moving_speed
        self.moving_range = moving_range
        self.initial_x = x
        self.break_timer = break_timer
        self.is_broken = False
        self.spring_power = 1.5 if platform_type == PlatformType.SPRING else 1.0
        
    def update(self, dt):
        if self.type == PlatformType.MOVING:
            # 左右移动平台逻辑
            self.x = self.initial_x + math.sin(self.moving_speed) * self.moving_range
        elif self.type == PlatformType.BREAKING and not self.is_broken:
            # 断裂平台计时
            self.break_timer -= dt
            if self.break_timer <= 0:
                self.is_broken = True
                
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, 10)

class Obstacle:
    def __init__(self, x, y, obstacle_type, width=20, height=20, 
                 moving_speed=0, moving_range=0, wind_strength=0):
        self.x = x
        self.y = y
        self.type = obstacle_type
        self.width = width
        self.height = height
        self.moving_speed = moving_speed
        self.moving_range = moving_range
        self.initial_x = x
        self.wind_strength = wind_strength
        
    def update(self, dt):
        if self.type == ObstacleType.MOVING_SPIKE:
            # 移动尖刺逻辑
            self.x = self.initial_x + math.sin(self.moving_speed) * self.moving_range
            
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class PlatformGenerator:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.platforms = []
        self.obstacles = []
        self.current_floor = 0
        self.min_platform_gap = 100  # 初始最小平台间距
        self.max_platform_gap = 150  # 初始最大平台间距
        
    def generate_floor(self, floor_number):
        """生成指定楼层的平台和障碍物"""
        self.current_floor = floor_number
        self.platforms = []
        self.obstacles = []
        
        # 随着楼层增加，调整平台间距
        gap_factor = 1 + (floor_number / 100) * 0.5
        self.min_platform_gap = int(100 * gap_factor)
        self.max_platform_gap = int(150 * gap_factor)
        
        # 起始平台
        start_platform = Platform(
            x=self.screen_width // 2 - 50,
            y=50,
            width=100,
            platform_type=PlatformType.NORMAL
        )
        self.platforms.append(start_platform)
        
        # 生成后续平台
        last_y = 50
        platform_count = random.randint(8, 12)  # 每层8-12个平台
        
        for i in range(platform_count):
            # 计算下一个平台的位置
            gap = random.randint(self.min_platform_gap, self.max_platform_gap)
            new_y = last_y + gap
            
            # 随机选择平台类型
            platform_type = self._get_random_platform_type(floor_number)
            
            # 根据平台类型设置属性
            if platform_type == PlatformType.NORMAL:
                width = random.randint(60, 120)
                moving_speed = 0
                moving_range = 0
                break_timer = 0
            elif platform_type == PlatformType.MOVING:
                width = random.randint(80, 100)
                moving_speed = random.uniform(1, 2)
                moving_range = random.randint(50, 100)
                break_timer = 0
            elif platform_type == PlatformType.BREAKING:
                width = random.randint(70, 110)
                moving_speed = 0
                moving_range = 0
                break_timer = random.uniform(2, 4)  # 2-4秒后断裂
            elif platform_type == PlatformType.SPRING:
                width = random.randint(60, 90)
                moving_speed = 0
                moving_range = 0
                break_timer = 0
                
            # 随机x位置，确保不会超出屏幕
            x = random.randint(0, self.screen_width - width)
            
            # 创建平台
            platform = Platform(
                x=x,
                y=new_y,
                width=width,
                platform_type=platform_type,
                moving_speed=moving_speed,
                moving_range=moving_range,
                break_timer=break_timer
            )
            self.platforms.append(platform)
            
            # 在平台上随机添加障碍物
            if random.random() < 0.3 + (floor_number / 200):  # 楼层越高，障碍物概率越大
                self._add_obstacle_to_platform(platform, floor_number)
                
            last_y = new_y
            
    def _get_random_platform_type(self, floor_number):
        """根据楼层随机选择平台类型"""
        # 随着楼层增加，特殊平台类型概率增加
        special_platform_chance = min(0.5, floor_number / 200)
        
        rand = random.random()
        if rand < 0.6:  # 60%普通平台
            return PlatformType.NORMAL
        elif rand < 0.8:  # 20%移动平台
            return PlatformType.MOVING
        elif rand < 0.9:  # 10%断裂平台
            return PlatformType.BREAKING
        elif rand < 0.95:  # 5%弹跳平台
            return PlatformType.SPRING
        else:  # 5%随机类型
            return random.choice(list(PlatformType))
            
    def _add_obstacle_to_platform(self, platform, floor_number):
        """在平台上添加障碍物"""
        obstacle_type = random.choice(list(ObstacleType))
        
        if obstacle_type == ObstacleType.SPIKE:
            # 普通尖刺
            x = random.randint(int(platform.x), int(platform.x + platform.width - 20))
            y = platform.y - 20
            obstacle = Obstacle(x, y, ObstacleType.SPIKE, width=20, height=20)
        elif obstacle_type == ObstacleType.MOVING_SPIKE:
            # 移动尖刺
            x = random.randint(int(platform.x), int(platform.x + platform.width - 20))
            y = platform.y - 20
            moving_speed = random.uniform(1, 2)
            moving_range = random.randint(30, 60)
            obstacle = Obstacle(
                x, y, ObstacleType.MOVING_SPIKE, 
                width=20, height=20,
                moving_speed=moving_speed,
                moving_range=moving_range
            )
        elif obstacle_type == ObstacleType.WIND:
            # 风力区域
            x = random.randint(int(platform.x), int(platform.x + platform.width - 40))
            y = platform.y - 40
            wind_strength = random.uniform(0.5, 1.5) * (1 + floor_number / 100)
            obstacle = Obstacle(
                x, y, ObstacleType.WIND,
                width=40, height=40,
                wind_strength=wind_strength
            )
            
        self.obstacles.append(obstacle)
        
    def update(self, dt):
        """更新所有平台和障碍物"""
        for platform in self.platforms:
            platform.update(dt)
            
        for obstacle in self.obstacles:
            obstacle.update(dt)
            
    def get_platform_at_position(self, x, y):
        """获取指定位置的平台"""
        for platform in self.platforms:
            if platform.get_rect().collidepoint(x, y):
                return platform
        return None
        
    def get_obstacle_at_position(self, x, y):
        """获取指定位置的障碍物"""
        for obstacle in self.obstacles:
            if obstacle.get_rect().collidepoint(x, y):
                return obstacle
        return None