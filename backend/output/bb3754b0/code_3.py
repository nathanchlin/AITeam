import random
import pygame

class Pipe:
    def __init__(self, screen_width, screen_height, gap_size=150, pipe_width=80, pipe_speed=5):
        """
        初始化管道对象
        
        参数:
            screen_width: 屏幕宽度
            screen_height: 屏幕高度
            gap_size: 管道间隙大小
            pipe_width: 管道宽度
            pipe_speed: 管道移动速度
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.gap_size = gap_size
        self.pipe_width = pipe_width
        self.pipe_speed = pipe_speed
        
        # 初始化管道位置
        self.x = screen_width
        self.gap_y = random.randint(gap_size//2, screen_height - gap_size//2)
        
        # 管道高度
        self.top_height = self.gap_y - gap_size//2
        self.bottom_height = screen_height - (self.gap_y + gap_size//2)
        
        # 管道颜色
        self.color = (0, 200, 0)
        
        # 标记是否已通过
        self.passed = False
    
    def update(self):
        """更新管道位置"""
        self.x -= self.pipe_speed
        
        # 更新管道高度
        self.top_height = self.gap_y - self.gap_size//2
        self.bottom_height = self.screen_height - (self.gap_y + self.gap_size//2)
    
    def draw(self, screen):
        """绘制管道"""
        # 绘制上管道
        pygame.draw.rect(screen, self.color, 
                         (self.x, 0, self.pipe_width, self.top_height))
        # 绘制下管道
        pygame.draw.rect(screen, self.color, 
                         (self.x, self.screen_height - self.bottom_height, 
                          self.pipe_width, self.bottom_height))
    
    def is_off_screen(self):
        """检查管道是否已离开屏幕"""
        return self.x + self.pipe_width < 0
    
    def collides_with(self, bird_rect):
        """检查管道是否与鸟碰撞"""
        # 创建管道矩形
        top_pipe_rect = pygame.Rect(self.x, 0, self.pipe_width, self.top_height)
        bottom_pipe_rect = pygame.Rect(self.x, self.screen_height - self.bottom_height, 
                                      self.pipe_width, self.bottom_height)
        
        # 检查碰撞
        return bird_rect.colliderect(top_pipe_rect) or bird_rect.colliderect(bottom_pipe_rect)
    
    def is_passed(self, bird_x):
        """检查鸟是否已通过管道"""
        if not self.passed and bird_x > self.x + self.pipe_width:
            self.passed = True
            return True
        return False