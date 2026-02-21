import pygame
import math

class InputHandler:
    def __init__(self, game_board):
        """
        初始化输入处理器
        
        参数:
            game_board: 游戏板实例，用于响应输入操作
        """
        self.game_board = game_board
        self.touch_start_pos = None
        self.min_swipe_distance = 50  # 最小滑动距离(像素)
        
    def handle_keyboard(self, key):
        """
        处理键盘输入
        
        参数:
            key: 按下的键
        """
        if key == pygame.K_UP or key == pygame.K_w:
            self.game_board.move('up')
        elif key == pygame.K_DOWN or key == pygame.K_s:
            self.game_board.move('down')
        elif key == pygame.K_LEFT or key == pygame.K_a:
            self.game_board.move('left')
        elif key == pygame.K_RIGHT or key == pygame.K_d:
            self.game_board.move('right')
        elif key == pygame.K_ESCAPE:
            self.game_board.toggle_pause()
        elif key == pygame.K_r:
            self.game_board.reset_game()
    
    def handle_touch_start(self, pos):
        """
        处理触摸开始事件
        
        参数:
            pos: 触摸位置 (x, y)
        """
        self.touch_start_pos = pos
    
    def handle_touch_end(self, pos):
        """
        处理触摸结束事件
        
        参数:
            pos: 触摸位置 (x, y)
        """
        if self.touch_start_pos:
            direction = self._calculate_swipe_direction(self.touch_start_pos, pos)
            if direction:
                self.game_board.move(direction)
            self.touch_start_pos = None
    
    def _calculate_swipe_direction(self, start_pos, end_pos):
        """
        计算滑动方向
        
        参数:
            start_pos: 开始位置 (x, y)
            end_pos: 结束位置 (x, y)
            
        返回:
            滑动方向 ('up', 'down', 'left', 'right') 或 None
        """
        dx = end_pos[0] - start_pos[0]
        dy = end_pos[1] - start_pos[1]
        
        # 计算距离
        distance = math.sqrt(dx**2 + dy**2)
        
        # 如果距离小于最小滑动距离，则不认为是滑动
        if distance < self.min_swipe_distance:
            return None
        
        # 确定主要移动方向
        if abs(dx) > abs(dy):
            # 水平移动
            return 'right' if dx > 0 else 'left'
        else:
            # 垂直移动
            return 'down' if dy > 0 else 'up'