def _is_game_over(self, board):
    """检查游戏是否结束"""
    # 检查是否有五连
    for i in range(self.board_size):
        for j in range(self.board_size):
            if board[i][j] != 0:
                if self._check_win(board, i, j):
                    return True
    return False

def _check_win(self, board, i, j):
    """检查从位置(i,j)出发是否有五连"""
    player = board[i][j]
    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]  # 水平、垂直、对角线
    
    for dx, dy in directions:
        count = 1  # 当前位置已经有一个棋子
        
        # 正方向检查
        x, y = i + dx, j + dy
        while 0 <= x < self.board_size and 0 <= y < self.board_size and board[x][y] == player:
            count += 1
            x += dx
            y += dy
            
        # 反方向检查
        x, y = i - dx, j - dy
        while 0 <= x < self.board_size and 0 <= y < self.board_size and board[x][y] == player:
            count += 1
            x -= dx
            y -= dy
            
        if count >= 5:
            return True
            
    return False