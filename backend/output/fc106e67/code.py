import pygame
import math

class Ninja:
    def __init__(self, x, y, game_width, game_height):
        # 初始化位置和尺寸
        self.x = x
        self.y = y
        self.width = 40
        self.height = 60
        self.game_width = game_width
        self.game_height = game_height
        
        # 移动属性
        self.velocity_x = 0
        self.velocity_y = 0
        self.speed = 5
        self.jump_power = 15
        self.gravity = 0.8
        
        # 状态管理
        self.is_jumping = False
        self.is_sliding = False
        self.is_facing_right = True
        
        # 动画相关
        self.animation_frame = 0
        self.animation_timer = 0
        self.animation_speed = 5
        
        # 滑行相关
        self.slide_duration = 0
        self.slide_max_duration = 30  # 滑行持续帧数
        self.slide_cool_down = 0
        
        # 地面高度
        self.ground_y = game_height - 100
        
        # 设置初始位置在地面
        self.y = self.ground_y - self.height