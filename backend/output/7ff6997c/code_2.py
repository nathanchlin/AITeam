import pygame
import math
import random

class Ninja:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 64
        self.height = 64
        self.vel_y = 0
        self.vel_x = 0
        self.is_jumping = False
        self.is_sliding = False
        self.is_attacking = False
        self.animation_frame = 0
        self.animation_timer = 0
        self.animation_speed = 5  # 帧切换速度
        
        # 加载精灵图
        self.spritesheet = pygame.image.load("ninja_spritesheet.png").convert_alpha()
        self.sprite_rects = create_ninja_spritesheet()
        
        # 当前动画状态
        self.state = "running"
        self.facing_right = True
        
        # 物理属性
        self.gravity = 0.8
        self.jump_strength = -15
        self.move_speed = 5
        self.slide_duration = 30  # 滑铲持续时间(帧)
        self.slide_timer = 0
        
    def update(self):
        # 更新动画帧
        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.animation_frame += 1
            
            # 检查动画是否需要循环
            if self.state == "running" and self.animation_frame >= 16:
                self.animation_frame = 0
            elif self.state == "jumping" and self.animation_frame >= 3:
                self.animation_frame = 0
            elif self.state == "attacking" and self.animation_frame >= 5:
                self.animation_frame = 0
                self.is_attacking = False
            elif self.state == "sliding" and self.animation_frame >= 2:
                self.animation_frame = 0
                
        # 更新物理状态
        if self.is_jumping:
            self.vel_y += self.gravity
            self.y += self.vel_y
            
            # 落地检测
            if self.y >= 300:  # 假设地面在y=300
                self.y = 300
                self.is_jumping = False
                self.vel_y = 0
                self.state = "running"
                
        # 更新滑铲状态
        if self.is_sliding:
            self.slide_timer += 1
            if self.slide_timer >= self.slide_duration:
                self.is_sliding = False
                self.slide_timer = 0
                self.height = 64  # 恢复正常高度
                
        # 水平移动
        self.x += self.vel_x
        
    def jump(self):
        if not self.is_jumping and not self.is_sliding:
            self.is_jumping = True
            self.vel_y = self.jump_strength
            self.state = "jumping"
            
    def slide(self):
        if not self.is_jumping and not self.is_sliding:
            self.is_sliding = True
            self.height = 32  # 滑铲时高度减半
            self.state = "sliding"
            self.slide_timer = 0
            
    def attack(self):
        if not self.is_attacking and not self.is_sliding:
            self.is_attacking = True
            self.state = "attacking"
            self.animation_frame = 0
            
    def draw(self, screen):
        # 获取当前帧的精灵图区域
        if self.state == "running":
            frame_rect = self.sprite_rects["running"][self.animation_frame]
        elif self.state == "jumping":
            frame_rect = self.sprite_rects["jumping"][self.animation_frame]
        elif self.state == "attacking":
            frame_rect = self.sprite_rects["attacking"][self.animation_frame]
        elif self.state == "sliding":
            frame_rect = self.sprite_rects["sliding"][self.animation_frame]
        else:
            frame_rect = self.sprite_rects["running"][0]
            
        # 绘制角色
        sprite = self.spritesheet.subsurface(frame_rect)
        
        # 如果面向左，翻转精灵图
        if not self.facing_right:
            sprite = pygame.transform.flip(sprite, True, False)
            
        # 调整滑铲时的绘制位置
        y_offset = 0
        if self.is_sliding:
            y_offset = 32  # 向上偏移以保持角色在地面
            
        screen.blit(sprite, (self.x, self.y - y_offset))
        
        # 如果正在攻击，绘制攻击效果
        if self.is_attacking:
            self.draw_attack_effect(screen)
            
    def draw_attack_effect(self, screen):
        # 根据当前攻击帧绘制不同的攻击效果
        if self.state == "attacking":
            if self.facing_right:
                sword_x = self.x + self.width + self.animation_frame * 3
                sword_y = self.y + 20
            else:
                sword_x = self.x - self.animation_frame * 3
                sword_y = self.y + 20
                
            # 绘制剑的光效
            for i in range(3):
                alpha = 255 - i * 80
                width = 4 - i
                pygame.draw.line(screen, (255, 255, 255, alpha), 
                               (sword_x - 5, sword_y - 5 + i*2), 
                               (sword_x + 5, sword_y - 5 + i*2), width)