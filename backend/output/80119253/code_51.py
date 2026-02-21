class GomokuAI:
    def __init__(self, difficulty='medium'):
        self.difficulty = difficulty
        self.max_depth = self._get_max_depth(difficulty)
        self.board_size = 15  # 标准五子棋棋盘大小
        
    def _get_max_depth(self, difficulty):
        """根据难度设置搜索深度"""
        depth_map = {
            'easy': 2,
            'medium': 4,
            'hard': 6,
            'expert': 8
        }
        return depth_map.get(difficulty, 4)
        
    def get_move(self, board):
        """根据当前棋盘状态返回AI的下一步移动"""
        if self.difficulty == 'easy':
            return self._get_random_move(board)
        else:
            return self._minimax_move(board)
            
    def _get_random_move(self, board):
        """简单难度：随机选择一个合法位置"""
        empty_positions = [(i, j) for i in range(self.board_size) 
                         for j in range(self.board_size) if board[i][j] == 0]
        return random.choice(empty_positions) if empty_positions else None
        
    def _minimax_move(self, board):
        """使用Minimax算法选择最佳移动"""
        best_score = float('-inf')
        best_move = None
        alpha = float('-inf')
        beta = float('inf')
        
        # 获取所有可能的移动（只考虑已有棋子周围的空位）
        possible_moves = self._get_possible_moves(board)
        
        for move in possible_moves:
            i, j = move
            board[i][j] = 2  # AI的棋子
            score = self._minimax(board, self.max_depth - 1, False, alpha, beta)
            board[i][j] = 0  # 撤销移动
            
            if score > best_score:
                best_score = score
                best_move = move
                
            alpha = max(alpha, best_score)
            
        return best_move
        
    def _minimax(self, board, depth, is_maximizing, alpha, beta):
        """Minimax算法与Alpha-Beta剪枝"""
        if depth == 0 or self._is_game_over(board):
            return self._evaluate_board(board)
            
        possible_moves = self._get_possible_moves(board)
        
        if is_maximizing:
            max_eval = float('-inf')
            for move in possible_moves:
                i, j = move
                board[i][j] = 2  # AI的棋子
                eval = self._minimax(board, depth - 1, False, alpha, beta)
                board[i][j] = 0  # 撤销移动
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for move in possible_moves:
                i, j = move
                board[i][j] = 1  # 玩家的棋子
                eval = self._minimax(board, depth - 1, True, alpha, beta)
                board[i][j] = 0  # 撤销移动
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval