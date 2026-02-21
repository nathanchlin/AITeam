# 初始化游戏板和碰撞检测器
BOARD_WIDTH = 10
BOARD_HEIGHT = 20
collision_detector = CollisionDetector(BOARD_WIDTH, BOARD_HEIGHT)

# 示例方块形状 (T形方块)
T_SHAPE = [
    [0, 1, 0],
    [1, 1, 1],
    [0, 0, 0]
]

# 更新游戏板状态 (假设已有一些方块放置)
game_board = np.zeros((BOARD_HEIGHT, BOARD_WIDTH), dtype=int)
# 添加一些已放置的方块
game_board[15:18, 4:7] = 1
collision_detector.update_board(game_board)

# 测试碰撞检测
print("初始位置碰撞检测:", collision_detector.check_collision(T_SHAPE, 4, 0))  # 应该返回False

# 测试移动
print("向右移动是否有效:", collision_detector.check_valid_move(T_SHAPE, 4, 0, dx=1, dy=0))  # 应该返回True
print("向左移动是否有效:", collision_detector.check_valid_move(T_SHAPE, 4, 0, dx=-1, dy=0))  # 应该返回True
print("向下移动是否有效:", collision_detector.check_valid_move(T_SHAPE, 4, 0, dx=0, dy=1))  # 应该返回True

# 测试旋转 (顺时针旋转90度)
def rotate_piece(piece):
    return [list(row) for row in zip(*piece[::-1])]

rotated_T = rotate_piece(T_SHAPE)
print("旋转后是否有效:", collision_detector.check_valid_rotation(T_SHAPE, 4, 0, rotated_T))  # 应该返回True

# 测试着陆
print("是否已经着陆:", collision_detector.check_landing(T_SHAPE, 4, 14))  # 应该返回True (因为下方有方块)