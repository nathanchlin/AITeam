# 创建游戏实例
game = GemMatchDetector(board_width=8, board_height=8)
game.initialize_board()

# 打印初始游戏板
print("初始游戏板:")
print(game.board)

# 尝试交换宝石
print("\n尝试交换宝石(0,0)和(0,1):")
if game.swap_gems(0, 0, 0, 1):
    print("交换成功，有匹配!")
else:
    print("交换失败，没有匹配")

# 打印交换后的游戏板
print("\n交换后的游戏板:")
print(game.board)
print(f"当前得分: {game.score}")