class GomokuChecker:
    def __init__(self, board_size=15):
        """
        初始化五子棋检测器
        :param board_size: 棋盘大小，默认15x15
        """
        self.board_size = board_size
        self.directions = [
            (0, 1),   # 横向
            (1, 0),   # 纵向
            (1, 1),   # 左斜
            (1, -1)   # 右斜
        ]
    
    def check_win(self, board, last_move):
        """
        检查是否有玩家获胜
        :param board: 棋盘状态
        :param last_move: 最后一步落子位置 (row, col)
        :return: 获胜玩家(1或2)或None(无人获胜)
        """
        if not last_move:
            return None
            
        row, col = last_move
        player = board[row][col]
        
        # 检查四个方向
        for dr, dc in self.directions:
            count = 1  # 包括刚下的棋子
            
            # 正向检查
            r, c = row + dr, col + dc
            while (0 <= r < self.board_size and 
                   0 <= c < self.board_size and 
                   board[r][c] == player):
                count += 1
                r += dr
                c += dc
            
            # 反向检查
            r, c = row - dr, col - dc
            while (0 <= r < self.board_size and 
                   0 <= c < self.board_size and 
                   board[r][c] == player):
                count += 1
                r -= dr
                c -= dc
            
            # 如果连续达到5个，则获胜
            if count >= 5:
                return player
        
        return None
    
    def check_draw(self, board):
        """
        检查是否平局
        :param board: 棋盘状态
        :return: True表示平局，False表示未平局
        """
        for row in board:
            if 0 in row:  # 还有空位
                return False
        return True
    
    def get_game_result(self, board, last_move=None):
        """
        获取游戏结果
        :param board: 棋盘状态
        :param last_move: 最后一步落子位置
        :return: (游戏状态, 获胜玩家)
                游戏状态: "win", "draw", "playing"
                获胜玩家: 1或2(仅当游戏状态为win时有效)
        """
        winner = self.check_win(board, last_move)
        if winner:
            return "win", winner
        
        if self.check_draw(board):
            return "draw", None
        
        return "playing", None