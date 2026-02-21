class GameObject:
    def __init__(self, x, y, layer="default"):
        self.x = x
        self.y = y
        self.layer = layer  # 碰撞层
        self.collision_mask = 0  # 碰撞掩码
        
    def can_collide_with(self, other):
        """检查是否可以与另一个物体碰撞"""
        return (self.collision_mask & other.layer) != 0