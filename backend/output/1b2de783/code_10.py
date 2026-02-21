import pygame
import sys
import random
import math
from enum import Enum

# 初始化Pygame
pygame.init()

# 游戏状态枚举
class GameState(Enum):
    MENU = 1
    PLAYING = 2
    PAUSED = 3
    GAME_OVER = 4

# 游戏配置
class GameConfig:
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    FPS = 60
    BACKGROUND_COLOR = (0, 0, 0)  # 黑色背景模拟太空
    PLAYER_SPEED = 5
    BULLET_SPEED = 7
    ASTEROID_MIN_SPEED = 1
    ASTEROID_MAX_SPEED = 3