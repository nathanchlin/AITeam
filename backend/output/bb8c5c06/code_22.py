def check_collision(snake):
    """检查碰撞条件"""
    # 获取蛇头位置
    head = snake[0]
    
    # 检查是否撞墙
    if (head[0] < 0 or head[0] >= GRID_WIDTH or 
        head[1] < 0 or head[1] >= GRID_HEIGHT):
        return True
    
    # 检查是否撞到自己（蛇身长度大于1时检查）
    if len(snake) > 2 and head in snake[1:]:
        return True
    
    return False