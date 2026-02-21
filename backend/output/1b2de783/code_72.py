import pygame
import random
import math
from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple, Optional

# 初始化Pygame
pygame.init()

# 游戏常量
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# 游戏状态枚举
class GameState(Enum):
    MENU = 1
    PLAYING = 2
    PAUSED = 3
    GAME_OVER = 4

# 游戏配置
@dataclass
class GameConfig:
    player_speed: float = 5.0
    bullet_speed: float = 10.0
    enemy_speed: float = 2.0
    enemy_spawn_rate: float = 0.02  # 每帧生成敌人的概率
    max_enemies: int = 10
    difficulty_increase_rate: float = 0.001  # 每帧难度增加率