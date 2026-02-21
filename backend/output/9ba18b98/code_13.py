# 创建游戏实例
game = TetrisGame()

# 生成一个T型方块
game.spawn_piece('T')

# 打印当前游戏状态
def print_board():
    board = game.board.copy()
    if game.current_piece:
        piece = game.pieces[game.current_piece][game.current_rotation]
        for y in range(len(piece)):
            for x in range(len(piece[0])):
                if piece[y][x]:
                    board_y = game.current_y + y
                    board_x = game.current_x + x
                    if 0 <= board_y < game.height and 0 <= board_x < game.width:
                        board[board_y][board_x] = 2  # 用2表示当前方块
    
    print("\n".join([" ".join(["#" if cell else "." for cell in row]) for row in board]))
    print()

print("初始状态:")
print_board()

# 顺时针旋转
game.rotate_piece(clockwise=True)
print("顺时针旋转后:")
print_board()

# 尝试墙踢（如果需要）
game.current_x -= 1  # 模拟靠近边界的情况
game.rotate_piece(clockwise=True)
print("尝试墙踢后:")
print_board()