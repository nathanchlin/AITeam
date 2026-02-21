# 示例使用
if __name__ == "__main__":
    # 假设游戏区域是20x10的格子
    detector = CollisionDetector(20, 10)
    
    # 测试撞墙检测
    # 蛇头在边界内
    print(detector.check_wall_collision((5, 5)))  # False
    # 蛇头在左边界外
    print(detector.check_wall_collision((-1, 5)))  # True
    # 蛇头在右边界外
    print(detector.check_wall_collision((20, 5)))  # True
    # 蛇头在下边界外
    print(detector.check_wall_collision((5, 10)))  # True
    
    # 测试撞自身检测
    # 蛇身坐标列表
    snake_body = [(5, 5), (5, 6), (5, 7), (5, 8)]
    # 蛇头没有撞到自身
    print(detector.check_self_collision((4, 5), snake_body))  # False
    # 蛇头撞到自身
    print(detector.check_self_collision((5, 6), snake_body))  # True
    
    # 综合测试
    # 正常情况
    print(detector.check_collision((5, 5), snake_body))  # False
    # 撞墙
    print(detector.check_collision((-1, 5), snake_body))  # True
    # 撞自身
    print(detector.check_collision((5, 6), snake_body))  # True