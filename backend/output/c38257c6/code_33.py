class SpecialBrick(Brick):
    def __init__(self, x, y, width, height, brick_type, color, hits=1, points=10):
        super().__init__(x, y, width, height, color, hits, points)
        self.brick_type = brick_type
        
    def hit(self):
        """特殊砖块被击中时的行为"""
        points = super().hit()
        if not self.is_active:
            return points, self.brick_type  # 返回额外信息
        return points, None

class BrickFactory:
    @staticmethod
    def create_brick(brick_type, x, y, width, height):
        """扩展的砖块创建方法"""
        if brick_type == "normal":
            return Brick(x, y, width, height, (255, 0, 0), hits=1, points=10)
        elif brick_type == "strong":
            return Brick(x, y, width, height, (0, 0, 255), hits=2, points=20)
        elif brick_type == "super":
            return Brick(x, y, width, height, (255, 215, 0), hits=3, points=30)
        elif brick_type == "unbreakable":
            return Brick(x, y, width, height, (128, 128, 128), hits=-1, points=0)
        elif brick_type == "explosive":
            return SpecialBrick(x, y, width, height, "explosive", (255, 100, 0), hits=1, points=15)
        elif brick_type == "multi_ball":
            return SpecialBrick(x, y, width, height, "multi_ball", (0, 255, 255), hits=1, points=25)
        elif brick_type == "slow_ball":
            return SpecialBrick(x, y, width, height, "slow_ball", (150, 0, 255), hits=1, points=20)
        else:
            return Brick(x, y, width, height, (255, 0, 0), hits=1, points=10)