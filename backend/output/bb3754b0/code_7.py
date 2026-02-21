def check_circle_rect_collision(circle_pos, circle_radius, rect):
    """
    检测圆形与矩形的碰撞
    :param circle_pos: 圆形中心坐标 (x, y)
    :param circle_radius: 圆形半径
    :param rect: 矩形 (x, y, width, height)
    :return: 如果碰撞返回True，否则返回False
    """
    # 找到矩形上距离圆心最近的点
    closest_x = max(rect[0], min(circle_pos[0], rect[0] + rect[2]))
    closest_y = max(rect[1], min(circle_pos[1], rect[1] + rect[3]))
    
    # 计算圆心到最近点的距离
    distance_x = circle_pos[0] - closest_x
    distance_y = circle_pos[1] - closest_y
    
    # 如果距离小于半径，则发生碰撞
    distance_squared = (distance_x ** 2) + (distance_y ** 2)
    return distance_squared < (circle_radius ** 2)