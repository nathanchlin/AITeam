# 创建游戏实例
game = GameState()

# 获取游戏信息
print(game.get_game_info())

# 落子示例
game.make_move(7, 7)  # 黑棋在中心落子
game.make_move(7, 8)  # 白棋在旁边落子

# 获取当前棋盘状态
board = game.get_board_state()
for row in board:
    print(row)

# 撤销一步
game.undo_move()

# 检查游戏状态
print(game.get_game_info())

# 获取所有可能的落子位置
possible_moves = game.get_possible_moves()
print(f"可能的落子位置数量: {len(possible_moves)}")