# 初始化AI
ai = GomokuAI(difficulty='medium')  # 可以是 'easy', 'medium', 'hard', 'expert'

# 在游戏循环中使用
board = [[0] * 15 for _ in range(15)]  # 15x15空棋盘

# 玩家下棋
player_move = (7, 7)  # 玩家下在中心
board[player_move[0]][player_move[1]] = 1

# AI下棋
ai_move = ai.get_move(board)
board[ai_move[0]][ai_move[1]] = 2