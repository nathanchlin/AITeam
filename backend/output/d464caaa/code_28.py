# 方块定义
class Tetromino:
    shape: List[List[int]]  # 方块形状矩阵
    color: Tuple[int, int, int]  # RGB颜色值
    x: int  # 当前x坐标
    y: int  # 当前y坐标
    rotation: int  # 旋转状态(0-3)

# 游戏状态
class GameState:
    board: List[List[int]]  # 游戏板状态
    current_piece: Tetromino  # 当前方块
    next_piece: Tetromino  # 下一个方块
    score: int  # 当前分数
    level: int  # 当前等级
    lines_cleared: int  # 已消除行数
    is_game_over: bool  # 游戏结束标志

# AI决策数据
class AIDecision:
    target_x: int  # 目标x位置
    target_rotation: int  # 目标旋转状态
    evaluation_score: float  # 评估分数