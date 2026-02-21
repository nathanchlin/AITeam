# 示例使用
if __name__ == "__main__":
    # 创建15x15的棋盘
    board_size = 15
    board = [[0 for _ in range(board_size)] for _ in range(board_size)]
    
    # 初始化检测器
    checker = GomokuChecker(board_size)
    
    # 模拟一些落子
    board[7][7] = 1  # 玩家1
    board[7][8] = 1
    board[7][9] = 1
    board[7][10] = 1
    board[7][11] = 1  # 横向五连
    
    # 检查游戏结果
    last_move = (7, 11)
    result, winner = checker.get_game_result(board, last_move)
    
    if result == "win":
        print(f"玩家 {winner} 获胜!")
    elif result == "draw":
        print("游戏平局!")
    else:
        print("游戏继续...")