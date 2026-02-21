def _evaluate_board(self, board):
    """评估当前棋盘状态，返回AI的得分"""
    ai_score = 0
    player_score = 0
    
    # 评估所有方向的棋型
    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]  # 水平、垂直、对角线
    
    for i in range(self.board_size):
        for j in range(self.board_size):
            if board[i][j] != 0:
                for dx, dy in directions:
                    pattern = self._get_pattern(board, i, j, dx, dy)
                    if pattern:
                        score = self._evaluate_pattern(pattern)
                        if board[i][j] == 2:  # AI的棋子
                            ai_score += score
                        else:  # 玩家的棋子
                            player_score += score
                            
    # 返回AI相对于玩家的得分
    return ai_score - player_score * 1.1  # 稍微重视防守

def _get_pattern(self, board, i, j, dx, dy):
    """获取某个方向上的棋型"""
    pattern = []
    player = board[i][j]
    
    # 向前和向后各取4个位置
    for step in range(-4, 5):
        x, y = i + step * dx, j + step * dy
        if 0 <= x < self.board_size and 0 <= y < self.board_size:
            pattern.append(board[x][y])
        else:
            pattern.append(-1)  # 边界外标记为-1
            
    return pattern

def _evaluate_pattern(self, pattern):
    """评估棋型并返回分数"""
    # 定义各种棋型的分数
    scores = {
        'five': 100000,    # 五连
        'open_four': 10000,  # 活四
        'four': 1000,      # 冲四
        'open_three': 1000,  # 活三
        'three': 100,      # 眠三
        'open_two': 100,   # 活二
        'two': 10,         # 眠二
        'one': 1           # 单子
    }
    
    # 检查五连
    if self._check_five(pattern):
        return scores['five']
        
    # 检查活四
    if self._check_open_four(pattern):
        return scores['open_four']
        
    # 检查冲四
    if self._check_four(pattern):
        return scores['four']
        
    # 检查活三
    if self._check_open_three(pattern):
        return scores['open_three']
        
    # 检查眠三
    if self._check_three(pattern):
        return scores['three']
        
    # 检查活二
    if self._check_open_two(pattern):
        return scores['open_two']
        
    # 检查眠二
    if self._check_two(pattern):
        return scores['two']
        
    # 检查单子
    if self._check_one(pattern):
        return scores['one']
        
    return 0

def _check_five(self, pattern):
    """检查是否有五连"""
    return 1 in pattern[5:10] and pattern[5] == 1 and all(p == 1 for p in pattern[5:10])

def _check_open_four(self, pattern):
    """检查是否有活四"""
    # 活四: 011110 或变体
    for i in range(1, 9):
        if pattern[i-1] == 0 and pattern[i] == 1 and pattern[i+1] == 1 and \
           pattern[i+2] == 1 and pattern[i+3] == 1 and pattern[i+4] == 0:
            return True
    return False

def _check_four(self, pattern):
    """检查是否有冲四"""
    # 冲四: 011112, 211110, 011101 等
    for i in range(1, 9):
        if (pattern[i] == 1 and pattern[i+1] == 1 and pattern[i+2] == 1 and 
            pattern[i+3] == 1 and pattern[i-1] != 0 and pattern[i+4] != 0):
            return True
    return False

def _check_open_three(self, pattern):
    """检查是否有活三"""
    # 活三: 01110, 011010, 010110 等
    for i in range(1, 9):
        if (pattern[i-1] == 0 and pattern[i] == 1 and pattern[i+1] == 1 and 
            pattern[i+2] == 1 and pattern[i+3] == 0):
            return True
        if (pattern[i-1] == 0 and pattern[i] == 1 and pattern[i+1] == 0 and 
            pattern[i+2] == 1 and pattern[i+3] == 1 and pattern[i+4] == 0):
            return True
        if (pattern[i-1] == 0 and pattern[i] == 1 and pattern[i+1] == 1 and 
            pattern[i+2] == 0 and pattern[i+3] == 1 and pattern[i+4] == 0):
            return True
    return False

def _check_three(self, pattern):
    """检查是否有眠三"""
    # 眠三: 11100, 00111, 11010, 01011 等
    for i in range(1, 9):
        if (pattern[i] == 1 and pattern[i+1] == 1 and pattern[i+2] == 1 and 
            pattern[i-1] != 0 and pattern[i+3] != 0):
            return True
    return False

def _check_open_two(self, pattern):
    """检查是否有活二"""
    # 活二: 01100, 00110, 01010 等
    for i in range(1, 9):
        if (pattern[i-1] == 0 and pattern[i] == 1 and pattern[i+1] == 1 and 
            pattern[i+2] == 0 and pattern[i+3] == 0):
            return True
        if (pattern[i-1] == 0 and pattern[i] == 1 and pattern[i+1] == 0 and 
            pattern[i+2] == 1 and pattern[i+3] == 0):
            return True
    return False

def _check_two(self, pattern):
    """检查是否有眠二"""
    # 眠二: 11000, 00110, 10100 等
    for i in range(1, 9):
        if (pattern[i] == 1 and pattern[i+1] == 1 and 
            pattern[i-1] != 0 and pattern[i+2] != 0):
            return True
    return False

def _check_one(self, pattern):
    """检查是否有单子"""
    return 1 in pattern