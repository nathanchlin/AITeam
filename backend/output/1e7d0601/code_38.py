def check_collision(obj1, obj2):
    """检测两个游戏对象是否碰撞"""
    if not (obj1.active and obj2.active):
        return False
    
    rect1 = obj1.get_rect()
    rect2 = obj2.get_rect()
    
    return rect1.colliderect(rect2)