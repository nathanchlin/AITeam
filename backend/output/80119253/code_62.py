# 优化前的评估函数示例
def evaluate_board(board):
    score = 0
    for i in range(15):
        for j in range(15):
            # 复杂的棋型判断逻辑
    return score

# 优化后的评估函数示例
def evaluate_board_optimized(board):
    # 使用位运算和预计算表
    patterns = precomputed_patterns
    score = 0
    # 使用位操作快速匹配棋型
    return score