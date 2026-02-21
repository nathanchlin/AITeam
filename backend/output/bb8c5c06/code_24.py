def reset_game():
    """重置游戏状态"""
    # 初始蛇的位置（水平居中，垂直居上）
    snake = [
        [GRID_WIDTH // 2, GRID_HEIGHT // 2],
        [GRID_WIDTH // 2 - 1, GRID_HEIGHT // 2],
        [GRID_WIDTH // 2 - 2, GRID_HEIGHT // 2]
    ]
    
    # 初始移动方向
    direction = [1, 0]  # 向右移动
    
    # 生成第一个食物
    food = generate_food(snake)
    
    # 初始分数
    score = 0
    
    return snake, direction, food, score

def generate_food(snake):
    """生成食物，确保不在蛇身上"""
    while True:
        food = [
            random.randint(0, GRID_WIDTH - 1),
            random.randint(0, GRID_HEIGHT - 1)
        ]
        if food not in snake:
            return food