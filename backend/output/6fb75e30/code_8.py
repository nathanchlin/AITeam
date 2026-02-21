class CollisionDetector:
    def __init__(self):
        self.character_box = None
        self.obstacle_boxes = []
    
    def update(self, character, obstacles):
        """更新碰撞检测数据"""
        self.character_box = Box(
            character.position,
            Vector2(CHARACTER_WIDTH, CHARACTER_HEIGHT)
        )
        self.obstacle_boxes = [obs.get_collision_box() for obs in obstacles if obs.active]
    
    def check_collisions(self):
        """检测碰撞"""
        collisions = []
        for i, box in enumerate(self.obstacle_boxes):
            if self._boxes_collide(self.character_box, box):
                collisions.append(i)
        return collisions
    
    def _boxes_collide(self, box1, box2):
        """两个矩形是否碰撞"""
        return (box1.position.x < box2.position.x + box2.size.x and
                box1.position.x + box1.size.x > box2.position.x and
                box1.position.y < box2.position.y + box2.size.y and
                box1.position.y + box1.size.y > box2.position.y)