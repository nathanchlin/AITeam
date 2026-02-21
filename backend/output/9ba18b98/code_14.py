import numpy as np

class CollisionDetector:
    def __init__(self, game_board_width, game_board_height):
        """
        初始化碰撞检测器
        
        参数:
            game_board_width: 游戏区域的宽度
            game_board_height: 游戏区域的高度
        """
        self.board_width = game_board_width
        self.board_height = game_board_height
        self.board = np.zeros((game_board_height, game_board_width), dtype=int)
    
    def update_board(self, board):
        """更新游戏板状态"""
        self.board = board.copy()
    
    def check_collision(self, piece, x, y):
        """
        检查方块在指定位置是否与边界或其他方块碰撞
        
        参数:
            piece: 当前方块形状 (二维数组)
            x: 方块在游戏板上的x坐标
            y: 方块在游戏板上的y坐标
            
        返回:
            bool: 如果发生碰撞返回True，否则返回False
        """
        for py, row in enumerate(piece):
            for px, cell in enumerate(row):
                if cell:  # 如果是方块的一部分
                    # 计算在游戏板上的实际位置
                    board_x = x + px
                    board_y = y + py
                    
                    # 检查边界
                    if (board_x < 0 or board_x >= self.board_width or 
                        board_y >= self.board_height):
                        return True
                    
                    # 检查是否与已放置的方块碰撞
                    if board_y >= 0 and self.board[board_y, board_x]:
                        return True
        
        return False
    
    def check_collision_with_rotation(self, piece, x, y, rotated_piece):
        """
        检查旋转后的方块是否与边界或其他方块碰撞
        
        参数:
            piece: 原始方块形状
            x: 方块在游戏板上的x坐标
            y: 方块在游戏板上的y坐标
            rotated_piece: 旋转后的方块形状
            
        返回:
            bool: 如果旋转后发生碰撞返回True，否则返回False
        """
        # 临时使用旋转后的形状进行碰撞检测
        return self.check_collision(rotated_piece, x, y)
    
    def check_valid_move(self, piece, x, y, dx=0, dy=0):
        """
        检查移动是否有效
        
        参数:
            piece: 当前方块形状
            x: 当前方块x坐标
            y: 当前方块y坐标
            dx: x方向移动量
            dy: y方向移动量
            
        返回:
            bool: 如果移动有效返回True，否则返回False
        """
        new_x = x + dx
        new_y = y + dy
        return not self.check_collision(piece, new_x, new_y)
    
    def check_valid_rotation(self, piece, x, y, rotated_piece):
        """
        检查旋转是否有效
        
        参数:
            piece: 当前方块形状
            x: 当前方块x坐标
            y: 当前方块y坐标
            rotated_piece: 旋转后的方块形状
            
        返回:
            bool: 如果旋转有效返回True，否则返回False
        """
        return not self.check_collision_with_rotation(piece, x, y, rotated_piece)
    
    def check_landing(self, piece, x, y):
        """
        检查方块是否已经着陆（无法再向下移动）
        
        参数:
            piece: 当前方块形状
            x: 当前方块x坐标
            y: 当前方块y坐标
            
        返回:
            bool: 如果已经着陆返回True，否则返回False
        """
        return not self.check_valid_move(piece, x, y, dx=0, dy=1)