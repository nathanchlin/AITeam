def _get_possible_moves(self, board):
    """获取所有可能的移动，只考虑已有棋子周围的空位"""
    moves = set()
    
    # 遍历棋盘，找到所有已有棋子
    for i in range(self.board_size):
        for j in range(self.board_size):
            if board[i][j] != 0:  # 如果有棋子
                # 检查周围2格内的空位
                for dx in range(-2, 3):
                    for dy in range(-2, 3):
                        x, y = i + dx, j + dy
                        if (0 <= x < self.board_size and 0 <= y < self.board_size and 
                            board[x][y] == 0):
                            moves.add((x, y))
                            
    # 如果棋盘为空，返回中心位置
    if not moves:
        center = self.board_size // 2
        return [(center, center)]
        
    return list(moves)