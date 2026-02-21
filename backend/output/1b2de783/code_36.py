def circle_collision(obj1, obj2):
    """检测两个圆形物体是否碰撞"""
    dx = obj1.x - obj2.x
    dy = obj1.y - obj2.y
    distance = math.sqrt(dx*dx + dy*dy)
    return distance < (obj1.radius + obj2.radius)