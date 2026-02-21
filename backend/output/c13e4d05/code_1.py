class Snake:
    def __init__(self):
        self.body = [(5, 5), (5, 6), (5, 7)]  # 初始蛇身
        self.grow_flag = False
        
class Food:
    def __init__(self):
        self.position = (0, 0)
        
class Direction:
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    
class GameState:
    RUNNING = 0
    PAUSED = 1
    GAME_OVER = 2