import pygame
from enum import Enum
from typing import List, Tuple

class BrickType(Enum):
    NORMAL = 1      # 普通砖块，一击消除
    HARD = 2        # 坚硬砖块，需要两次击打
    UNBREAKABLE = 3 # 不可破坏砖块
    EXPLOSIVE = 4   # 爆炸砖块，消除时会影响周围砖块
    BONUS = 5       # 奖励砖块，消除后获得特殊效果

class Brick:
    def __init__(self, x: int, y: int, width: int, height: int, brick_type: BrickType):
        self.rect = pygame.Rect(x, y, width, height)
        self.type = brick_type
        self.hits = 1 if brick_type != BrickType.HARD else 2
        self.max_hits = self.hits
        self.color = self._get_color()
        self.is_destroyed = False
        
    def _get_color(self) -> Tuple[int, int, int]:
        """根据砖块类型返回颜色"""
        color_map = {
            BrickType.NORMAL: (200, 200, 200),    # 灰色
            BrickType.HARD: (150, 150, 150),       # 深灰色
            BrickType.UNBREAKABLE: (100, 100, 100), # 更深的灰色
            BrickType.EXPLOSIVE: (255, 100, 100),  # 红色
            BrickType.BONUS: (100, 255, 100)       # 绿色
        }
        return color_map.get(self.type, (200, 200, 200))
    
    def hit(self) -> bool:
        """砖块被击中，返回是否被消除"""
        if self.type == BrickType.UNBREAKABLE:
            return False
            
        if self.type == BrickType.HARD:
            self.hits -= 1
            self.color = self._get_color()  # 更新颜色表示受损状态
            return self.hits <= 0
        else:
            self.is_destroyed = True
            return True
    
    def draw(self, screen: pygame.Surface):
        """绘制砖块"""
        if not self.is_destroyed:
            pygame.draw.rect(screen, self.color, self.rect)
            pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)  # 边框
            
            # 为不同类型砖块添加标识
            if self.type == BrickType.HARD and self.hits > 1:
                font = pygame.font.SysFont(None, 20)
                text = font.render(str(self.hits), True, (255, 255, 255))
                text_rect = text.get_rect(center=self.rect.center)
                screen.blit(text, text_rect)