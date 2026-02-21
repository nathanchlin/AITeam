import numpy as np
from collections import deque

class GemMatchDetector:
    def __init__(self, board_width=8, board_height=8):
        self.board_width = board_width
        self.board_height = board_height
        self.board = np.zeros((board_height, board_width), dtype=int)
        self.gem_types = 5  # 宝石种类数
        self.score = 0
        self.combo_count = 0
        
    def initialize_board(self):
        """初始化游戏板，随机放置宝石"""
        for row in range(self.board_height):
            for col in range(self.board_width):
                self.board[row][col] = np.random.randint(1, self.gem_types + 1)
        
        # 确保初始状态没有匹配
        while self.find_all_matches():
            self.resolve_matches()
    
    def find_all_matches(self):
        """查找所有匹配并返回匹配位置"""
        matches = []
        
        # 检查水平匹配
        for row in range(self.board_height):
            for col in range(self.board_width - 2):
                if self.board[row][col] != 0 and \
                   self.board[row][col] == self.board[row][col+1] == self.board[row][col+2]:
                    match_length = 3
                    # 检查是否有更长的匹配
                    while col + match_length < self.board_width and \
                          self.board[row][col] == self.board[row][col + match_length]:
                        match_length += 1
                    matches.append({
                        'type': 'horizontal',
                        'row': row,
                        'col': col,
                        'length': match_length,
                        'gem_type': self.board[row][col]
                    })
        
        # 检查垂直匹配
        for col in range(self.board_width):
            for row in range(self.board_height - 2):
                if self.board[row][col] != 0 and \
                   self.board[row][col] == self.board[row+1][col] == self.board[row+2][col]:
                    match_length = 3
                    # 检查是否有更长的匹配
                    while row + match_length < self.board_height and \
                          self.board[row][col] == self.board[row + match_length][col]:
                        match_length += 1
                    matches.append({
                        'type': 'vertical',
                        'row': row,
                        'col': col,
                        'length': match_length,
                        'gem_type': self.board[row][col]
                    })
        
        # 检查特殊形状匹配（L形、T形等）
        special_matches = self.find_special_matches()
        matches.extend(special_matches)
        
        return matches
    
    def find_special_matches(self):
        """查找特殊形状的匹配（L形、T形等）"""
        matches = []
        
        # 检查L形匹配
        for row in range(self.board_height - 2):
            for col in range(self.board_width - 2):
                center_gem = self.board[row][col]
                if center_gem == 0:
                    continue
                
                # 检查右下L形
                if (center_gem == self.board[row][col+1] == self.board[row][col+2] and
                    center_gem == self.board[row+1][col] == self.board[row+2][col]):
                    matches.append({
                        'type': 'L_right_down',
                        'row': row,
                        'col': col,
                        'length': 5,
                        'gem_type': center_gem
                    })
                
                # 检查左下L形
                if (center_gem == self.board[row][col+1] == self.board[row][col+2] and
                    center_gem == self.board[row+1][col+2] == self.board[row+2][col+2]):
                    matches.append({
                        'type': 'L_left_down',
                        'row': row,
                        'col': col,
                        'length': 5,
                        'gem_type': center_gem
                    })
                
                # 检查右上L形
                if (center_gem == self.board[row+1][col] == self.board[row+2][col] and
                    center_gem == self.board[row][col+1] == self.board[row][col+2]):
                    matches.append({
                        'type': 'L_right_up',
                        'row': row,
                        'col': col,
                        'length': 5,
                        'gem_type': center_gem
                    })
                
                # 检查左上L形
                if (center_gem == self.board[row+1][col] == self.board[row+2][col] and
                    center_gem == self.board[row+2][col+1] == self.board[row+2][col+2]):
                    matches.append({
                        'type': 'L_left_up',
                        'row': row,
                        'col': col,
                        'length': 5,
                        'gem_type': center_gem
                    })
        
        # 检查T形匹配
        for row in range(1, self.board_height - 1):
            for col in range(1, self.board_width - 1):
                center_gem = self.board[row][col]
                if center_gem == 0:
                    continue
                
                # 检查上T形
                if (center_gem == self.board[row][col-1] == self.board[row][col+1] and
                    center_gem == self.board[row+1][col]):
                    matches.append({
                        'type': 'T_up',
                        'row': row,
                        'col': col,
                        'length': 4,
                        'gem_type': center_gem
                    })
                
                # 检查下T形
                if (center_gem == self.board[row][col-1] == self.board[row][col+1] and
                    center_gem == self.board[row-1][col]):
                    matches.append({
                        'type': 'T_down',
                        'row': row,
                        'col': col,
                        'length': 4,
                        'gem_type': center_gem
                    })
                
                # 检查左T形
                if (center_gem == self.board[row-1][col] == self.board[row+1][col] and
                    center_gem == self.board[row][col+1]):
                    matches.append({
                        'type': 'T_left',
                        'row': row,
                        'col': col,
                        'length': 4,
                        'gem_type': center_gem
                    })
                
                # 检查右T形
                if (center_gem == self.board[row-1][col] == self.board[row+1][col] and
                    center_gem == self.board[row][col-1]):
                    matches.append({
                        'type': 'T_right',
                        'row': row,
                        'col': col,
                        'length': 4,
                        'gem_type': center_gem
                    })
        
        return matches
    
    def resolve_matches(self, matches=None):
        """处理匹配，消除宝石并计算得分"""
        if matches is None:
            matches = self.find_all_matches()
        
        if not matches:
            return False
        
        # 标记要消除的宝石
        marked_to_remove = set()
        for match in matches:
            if match['type'] == 'horizontal':
                for i in range(match['length']):
                    marked_to_remove.add((match['row'], match['col'] + i))
            elif match['type'] == 'vertical':
                for i in range(match['length']):
                    marked_to_remove.add((match['row'] + i, match['col']))
            elif match['type'] == 'L_right_down':
                # 水平部分
                for i in range(3):
                    marked_to_remove.add((match['row'], match['col'] + i))
                # 垂直部分
                for i in range(3):
                    marked_to_remove.add((match['row'] + i, match['col']))
            elif match['type'] == 'L_left_down':
                # 水平部分
                for i in range(3):
                    marked_to_remove.add((match['row'], match['col'] + i))
                # 垂直部分
                for i in range(3):
                    marked_to_remove.add((match['row'] + i, match['col'] + 2))
            elif match['type'] == 'L_right_up':
                # 水平部分
                for i in range(3):
                    marked_to_remove.add((match['row'], match['col'] + i))
                # 垂直部分
                for i in range(3):
                    marked_to_remove.add((match['row'] + i, match['col']))
            elif match['type'] == 'L_left_up':
                # 水平部分
                for i in range(3):
                    marked_to_remove.add((match['row'] + 2, match['col'] + i))
                # 垂直部分
                for i in range(3):
                    marked_to_remove.add((match['row'] + i, match['col']))
            elif match['type'] == 'T_up':
                # 水平部分
                marked_to_remove.add((match['row'], match['col'] - 1))
                marked_to_remove.add((match['row'], match['col']))
                marked_to_remove.add((match['row'], match['col'] + 1))
                # 垂直部分
                marked_to_remove.add((match['row'] + 1, match['col']))
            elif match['type'] == 'T_down':
                # 水平部分
                marked_to_remove.add((match['row'], match['col'] - 1))
                marked_to_remove.add((match['row'], match['col']))
                marked_to_remove.add((match['row'], match['col'] + 1))
                # 垂直部分
                marked_to_remove.add((match['row'] - 1, match['col']))
            elif match['type'] == 'T_left':
                # 垂直部分
                marked_to_remove.add((match['row'] - 1, match['col']))
                marked_to_remove.add((match['row'], match['col']))
                marked_to_remove.add((match['row'] + 1, match['col']))
                # 水平部分
                marked_to_remove.add((match['row'], match['col'] + 1))
            elif match['type'] == 'T_right':
                # 垂直部分
                marked_to_remove.add((match['row'] - 1, match['col']))
                marked_to_remove.add((match['row'], match['col']))
                marked_to_remove.add((match['row'] + 1, match['col']))
                # 水平部分
                marked_to_remove.add((match['row'], match['col'] - 1))
        
        # 计算得分
        for match in matches:
            if match['type'] in ['horizontal', 'vertical']:
                base_score = 10 * match['length']
                self.score += base_score * (1 + self.combo_count * 0.5)
            elif match['type'].startswith('L_'):
                base_score = 25  # L形基础得分
                self.score += base_score * (1 + self.combo_count * 0.5)
            elif match['type'].startswith('T_'):
                base_score = 20  # T形基础得分
                self.score += base_score * (1 + self.combo_count * 0.5)
        
        # 消除宝石
        for row, col in marked_to_remove:
            self.board[row][col] = 0
        
        # 宝石下落
        self.drop_gems()
        
        # 填充新宝石
        self.fill_empty_cells()
        
        # 增加连击计数
        self.combo_count += 1
        
        # 检查是否有新的匹配
        new_matches = self.find_all_matches()
        if new_matches:
            # 递归处理连锁反应
            self.resolve_matches(new_matches)
        else:
            # 重置连击计数
            self.combo_count = 0
        
        return True
    
    def drop_gems(self):
        """使宝石下落填充空位"""
        for col in range(self.board_width):
            # 从底部向上扫描每一列
            empty_row = self.board_height - 1
            for row in range(self.board_height - 1, -1, -1):
                if self.board[row][col] != 0:
                    if row != empty_row:
                        self.board[empty_row][col] = self.board[row][col]
                        self.board[row][col] = 0
                    empty_row -= 1
    
    def fill_empty_cells(self):
        """用新宝石填充空位"""
        for col in range(self.board_width):
            for row in range(self.board_height):
                if self.board[row][col] == 0:
                    self.board[row][col] = np.random.randint(1, self.gem_types + 1)
    
    def swap_gems(self, row1, col1, row2, col2):
        """交换两个宝石的位置"""
        if self.is_valid_swap(row1, col1, row2, col2):
            self.board[row1][col1], self.board[row2][col2] = \
                self.board[row2][col2], self.board[row1][col1]
            
            # 检查交换后是否有匹配
            matches = self.find_all_matches()
            if matches:
                self.resolve_matches(matches)
                return True
            else:
                # 如果没有匹配，交换回来
                self.board[row1][col1], self.board[row2][col2] = \
                    self.board[row2][col2], self.board[row1][col1]
                return False
        return False
    
    def is_valid_swap(self, row1, col1, row2, col2):
        """检查交换是否有效（相邻位置）"""
        if not (0 <= row1 < self.board_height and 0 <= col1 < self.board_width and
                0 <= row2 < self.board_height and 0 <= col2 < self.board_width):
            return False
        
        # 检查是否相邻
        if abs(row1 - row2) + abs(col1 - col2) != 1:
            return False
        
        return True