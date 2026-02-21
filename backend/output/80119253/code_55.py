def _iterative_deepening_minimax(self, board):
    """迭代深化Minimax搜索"""
    best_move = None
    for depth in range(1, self.max_depth + 1):
        _, move = self._minimax_with_depth(board, depth)
        if move:
            best_move = move
    return best_move

def _minimax_with_depth(self, board, depth):
    """带深度限制的Minimax搜索"""
    best_score = float('-inf')
    best_move = None
    alpha = float('-inf')
    beta = float('inf')
    
    possible_moves = self._get_possible_moves(board)
    
    for move in possible_moves:
        i, j = move
        board[i][j] = 2  # AI的棋子
        score = self._minimax(board, depth - 1, False, alpha, beta)
        board[i][j] = 0  # 撤销移动
        
        if score > best_score:
            best_score = score
            best_move = move
            
        alpha = max(alpha, best_score)
        
    return best_score, best_move