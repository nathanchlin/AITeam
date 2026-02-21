class CollisionDetector:
    def __init__(self):
        pass
    
    def check_aabb_collision(self, rect1, rect2):
        """
        检测两个矩形是否碰撞
        :param rect1: 第一个矩形 (x, y, width, height)
        :param rect2: 第二个矩形 (x, y, width, height)
        :return: 如果碰撞返回True，否则返回False
        """
        x1, y1, w1, h1 = rect1
        x2, y2, w2, h2 = rect2
        
        # 检查矩形是否重叠
        if (x1 < x2 + w2 and
            x1 + w1 > x2 and
            y1 < y2 + h2 and
            y1 + h1 > y2):
            return True
        
        return False