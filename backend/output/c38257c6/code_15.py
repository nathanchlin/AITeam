import pygame
import sys

class PaddleController:
    def __init__(self, paddle_speed=8):
        """
        初始化挡板控制器
        
        参数:
            paddle_speed: 挡板移动速度(像素/帧)
        """
        self.paddle_speed = paddle_speed
        self.key_states = {
            pygame.K_LEFT: False,
            pygame.K_RIGHT: False
        }
        self.active_keys = []
        
        # 添加键盘事件监听
        pygame.key.set_repeat(100, 20)  # 初始延迟100ms，后续间隔20ms
        
    def handle_event(self, event):
        """
        处理键盘事件
        
        参数:
            event: pygame事件对象
        """
        if event.type == pygame.KEYDOWN:
            if event.key in self.key_states:
                self.key_states[event.key] = True
                if event.key not in self.active_keys:
                    self.active_keys.append(event.key)
                    
        elif event.type == pygame.KEYUP:
            if event.key in self.key_states:
                self.key_states[event.key] = False
                if event.key in self.active_keys:
                    self.active_keys.remove(event.key)
    
    def update(self, paddle_rect, screen_width):
        """
        更新挡板位置
        
        参数:
            paddle_rect: 挡板的矩形对象
            screen_width: 屏幕宽度(用于边界检测)
            
        返回:
            更新后的挡板矩形对象
        """
        # 计算移动方向
        move_x = 0
        if self.key_states[pygame.K_LEFT]:
            move_x -= self.paddle_speed
        if self.key_states[pygame.K_RIGHT]:
            move_x += self.paddle_speed
            
        # 应用移动
        paddle_rect.x += move_x
        
        # 边界检测
        if paddle_rect.left < 0:
            paddle_rect.left = 0
        elif paddle_rect.right > screen_width:
            paddle_rect.right = screen_width
            
        return paddle_rect
    
    def set_speed(self, new_speed):
        """设置挡板移动速度"""
        self.paddle_speed = new_speed
        
    def get_active_keys(self):
        """获取当前按下的键列表"""
        return self.active_keys.copy()