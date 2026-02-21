def evaluate_board(board, current_piece, next_piece):
       score = 0
       # 消行潜力
       score += calculate_clear_potential(board, current_piece) * 0.4
       # 高度平衡
       score += calculate_height_balance(board) * 0.3
       # 凹洞数量
       score -= calculate_holes(board) * 0.2
       # 预见性（考虑下一个方块）
       score += calculate_next_piece_fit(board, next_piece) * 0.1
       return score