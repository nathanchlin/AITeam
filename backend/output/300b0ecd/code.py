import pygame
import math

class Ninja:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 32
        self.height = 48
        self.vel_y = 0
        self.jumping = False
        self.facing_right = True
        self.animation_state = "idle"
        self.frame_count = 0
        self.frame_delay = 10
        self.current_frame = 0
        
        # 动画帧定义
        self.animations = {
            "idle": [
                # 站立帧1
                [
                    (0, 0, 16, 48),  # 头部
                    (4, 16, 8, 24),  # 身体
                    (0, 24, 4, 8),   # 左腿
                    (12, 24, 4, 8),  # 右腿
                    (2, 12, 3, 4),   # 左臂
                    (11, 12, 3, 4)   # 右臂
                ],
                # 站立帧2（轻微呼吸效果）
                [
                    (0, 0, 16, 48),  # 头部
                    (4, 16, 8, 24),  # 身体
                    (0, 24, 4, 8),   # 左腿
                    (12, 24, 4, 8),  # 右腿
                    (2, 12, 3, 4),   # 左臂
                    (11, 12, 3, 4),  # 右臂
                    (6, 8, 4, 4)     # 呼吸效果
                ]
            ],
            "run": [
                # 跑步帧1
                [
                    (0, 0, 16, 48),  # 头部
                    (4, 16, 8, 24),  # 身体
                    (0, 24, 4, 8),   # 左腿（后）
                    (12, 24, 4, 8),  # 右腿（前）
                    (2, 12, 3, 4),   # 左臂（摆动）
                    (11, 12, 3, 4)   # 右臂（摆动）
                ],
                # 跑步帧2
                [
                    (0, 0, 16, 48),  # 头部
                    (4, 16, 8, 24),  # 身体
                    (4, 24, 4, 8),   # 左腿（前）
                    (8, 24, 4, 8),   # 右腿（后）
                    (2, 12, 3, 4),   # 左臂（摆动）
                    (11, 12, 3, 4)   # 右臂（摆动）
                ]
            ],
            "jump": [
                # 跳跃帧
                [
                    (0, 0, 16, 48),  # 头部
                    (4, 16, 8, 24),  # 身体
                    (2, 24, 4, 8),   # 左腿（弯曲）
                    (10, 24, 4, 8),  # 右腿（弯曲）
                    (0, 12, 3, 4),   # 左臂（上举）
                    (13, 12, 3, 4)   # 右臂（上举）
                ]
            ],
            "attack": [
                # 攻击帧1
                [
                    (0, 0, 16, 48),  # 头部
                    (4, 16, 8, 24),  # 身体
                    (0, 24, 4, 8),   # 左腿
                    (12, 24, 4, 8),  # 右腿
                    (2, 12, 6, 4),   # 左臂（持剑）
                    (11, 12, 3, 4)   # 右臂
                ],
                # 攻击帧2（出剑）
                [
                    (0, 0, 16, 48),  # 头部
                    (4, 16, 8, 24),  # 身体
                    (0, 24, 4, 8),   # 左腿
                    (12, 24, 4, 8),  # 右腿
                    (2, 12, 10, 4),  # 左臂（出剑）
                    (11, 12, 3, 4)   # 右臂
                ]
            ]
        }
        
        # 创建角色精灵表面
        self.sprite_sheet = pygame.Surface((64, 64), pygame.SRCALPHA)
        self.create_sprite_sheet()
        
    def create_sprite_sheet(self):
        """创建精灵表，包含所有动画帧"""
        # 绘制绿色忍者
        green = (0, 200, 0)  # 主绿色
        dark_green = (0, 150, 0)  # 深绿色（阴影）
        lighter_green = (100, 255, 100)  # 浅绿色（高光）
        
        # 绘制头部
        pygame.draw.rect(self.sprite_sheet, green, (8, 0, 16, 16))
        pygame.draw.rect(self.sprite_sheet, dark_green, (8, 0, 16, 8))  # 头部阴影
        
        # 绘制眼睛
        pygame.draw.rect(self.sprite_sheet, (0, 0, 0), (10, 4, 2, 2))
        pygame.draw.rect(self.sprite_sheet, (0, 0, 0), (18, 4, 2, 2))
        
        # 绘制身体
        pygame.draw.rect(self.sprite_sheet, green, (12, 16, 8, 20))
        pygame.draw.rect(self.sprite_sheet, dark_green, (12, 16, 8, 10))  # 身体阴影
        
        # 绘制腿部
        pygame.draw.rect(self.sprite_sheet, green, (8, 36, 4, 8))
        pygame.draw.rect(self.sprite_sheet, green, (20, 36, 4, 8))
        
        # 绘制手臂
        pygame.draw.rect(self.sprite_sheet, green, (6, 20, 3, 8))
        pygame.draw.rect(self.sprite_sheet, green, (23, 20, 3, 8))
        
        # 绘制忍者刀（第二套动画）
        pygame.draw.rect(self.sprite_sheet, (200, 200, 200), (28, 16, 20, 2))
        pygame.draw.rect(self.sprite_sheet, (150, 150, 150), (28, 16, 20, 2), 1)
        
    def update(self):
        """更新角色状态和动画"""
        # 更新动画帧
        self.frame_count += 1
        if self.frame_count >= self.frame_delay:
            self.frame_count = 0
            self.current_frame = (self.current_frame + 1) % len(self.animations[self.animation_state])
        
        # 重力
        if self.jumping:
            self.vel_y += 0.8
            self.y += self.vel_y
            
            if self.y >= 300:  # 地面位置
                self.y = 300
                self.jumping = False
                self.vel_y = 0
                self.animation_state = "run"
    
    def jump(self):
        """跳跃动作"""
        if not self.jumping:
            self.jumping = True
            self.vel_y = -15
            self.animation_state = "jump"
    
    def attack(self):
        """攻击动作"""
        self.animation_state = "attack"
        # 攻击结束后回到跑步状态
        pygame.time.set_timer(pygame.USEREVENT + 1, 300)
    
    def draw(self, screen):
        """绘制角色"""
        # 获取当前动画帧
        current_animation = self.animations[self.animation_state]
        current_frame = current_animation[self.current_frame]
        
        # 创建临时表面用于绘制当前帧
        frame_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # 绘制每个部分
        for part in current_frame:
            x, y, w, h = part
            # 从精灵表中复制部分
            part_surface = self.sprite_sheet.subsurface((x, y, w, h))
            frame_surface.blit(part_surface, (x, y))
        
        # 如果面向左侧，翻转图像
        if not self.facing_right:
            frame_surface = pygame.transform.flip(frame_surface, True, False)
        
        # 绘制到屏幕
        screen.blit(frame_surface, (self.x, self.y))