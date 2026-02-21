import numpy as np

class TetrisGame:
    def __init__(self, width=10, height=20):
        self.width = width
        self.height = height
        self.board = np.zeros((height, width), dtype=int)
        self.current_piece = None
        self.current_x = 0
        self.current_y = 0
        self.current_rotation = 0
        
        # 定义所有方块的形状（包括所有旋转状态）
        self.pieces = {
            'I': [
                [[1, 1, 1, 1]],
                [[1], [1], [1], [1]]
            ],
            'O': [
                [[1, 1],
                 [1, 1]]
            ],
            'T': [
                [[0, 1, 0],
                 [1, 1, 1]],
                [[1, 0],
                 [1, 1],
                 [1, 0]],
                [[1, 1, 1],
                 [0, 1, 0]],
                [[0, 1],
                 [1, 1],
                 [0, 1]]
            ],
            'S': [
                [[0, 1, 1],
                 [1, 1, 0]],
                [[1, 0],
                 [1, 1],
                 [0, 1]]
            ],
            'Z': [
                [[1, 1, 0],
                 [0, 1, 1]],
                [[0, 1],
                 [1, 1],
                 [1, 0]]
            ],
            'J': [
                [[1, 0, 0],
                 [1, 1, 1]],
                [[1, 1],
                 [1, 0],
                 [1, 0]],
                [[1, 1, 1],
                 [0, 0, 1]],
                [[0, 1],
                 [0, 1],
                 [1, 1]]
            ],
            'L': [
                [[0, 0, 1],
                 [1, 1, 1]],
                [[1, 0],
                 [1, 0],
                 [1, 1]],
                [[1, 1, 1],
                 [1, 0, 0]],
                [[1, 1],
                 [0, 1],
                 [0, 1]]
            ]
        }
    
    def spawn_piece(self, piece_type):
        """生成新方块"""
        self.current_piece = piece_type
        self.current_rotation = 0
        self.current_x = self.width // 2 - len(self.pieces[piece_type][0][0]) // 2
        self.current_y = 0
        
        # 检查游戏是否结束
        if self.check_collision():
            return False
        return True
    
    def rotate_piece(self, clockwise=True):
        """旋转当前方块"""
        if not self.current_piece:
            return False
        
        # 获取当前方块的旋转状态
        rotations = self.pieces[self.current_piece]
        current_rotation_state = rotations[self.current_rotation]
        
        # 计算下一个旋转状态
        if clockwise:
            next_rotation = (self.current_rotation + 1) % len(rotations)
        else:
            next_rotation = (self.current_rotation - 1) % len(rotations)
        
        next_rotation_state = rotations[next_rotation]
        
        # 尝试直接旋转
        if self.can_rotate_to(next_rotation_state):
            self.current_rotation = next_rotation
            return True
        
        # 如果直接旋转失败，尝试墙踢
        return self.wall_kick(current_rotation_state, next_rotation_state)
    
    def can_rotate_to(self, rotation_state):
        """检查是否可以旋转到指定状态"""
        piece_height = len(rotation_state)
        piece_width = len(rotation_state[0])
        
        # 检查边界
        if (self.current_x < 0 or 
            self.current_x + piece_width > self.width or 
            self.current_y + piece_height > self.height):
            return False
        
        # 检查与已固定方块的碰撞
        for y in range(piece_height):
            for x in range(piece_width):
                if rotation_state[y][x] and self.board[self.current_y + y][self.current_x + x]:
                    return False
        
        return True
    
    def wall_kick(self, current_state, next_state):
        """墙踢机制，尝试在无法直接旋转时偏移位置"""
        # 定义可能的偏移量（基于SRS旋转系统）
        kicks = [
            (0, 0),  # 不偏移
            (-1, 0), (1, 0),  # 水平偏移
            (0, -1), (0, 1),  # 垂直偏移
            (-1, -1), (1, -1),  # 对角线偏移
            (-1, 1), (1, 1)  # 对角线偏移
        ]
        
        for dx, dy in kicks:
            if dx == 0 and dy == 0:
                continue  # 已经检查过直接旋转
            
            # 尝试偏移
            old_x, old_y = self.current_x, self.current_y
            self.current_x += dx
            self.current_y += dy
            
            if self.can_rotate_to(next_state):
                self.current_rotation = (self.current_rotation + 1) % len(self.pieces[self.current_piece]) if dx > 0 else (self.current_rotation - 1) % len(self.pieces[self.current_piece])
                return True
            
            # 恢复位置
            self.current_x, self.current_y = old_x, old_y
        
        return False
    
    def check_collision(self):
        """检查当前方块是否与边界或其他方块碰撞"""
        if not self.current_piece:
            return False
        
        piece_state = self.pieces[self.current_piece][self.current_rotation]
        piece_height = len(piece_state)
        piece_width = len(piece_state[0])
        
        for y in range(piece_height):
            for x in range(piece_width):
                if piece_state[y][x]:
                    board_y = self.current_y + y
                    board_x = self.current_x + x
                    
                    # 检查边界
                    if board_x < 0 or board_x >= self.width or board_y >= self.height:
                        return True
                    
                    # 检查与已固定方块的碰撞
                    if board_y >= 0 and self.board[board_y][board_x]:
                        return True
        
        return False