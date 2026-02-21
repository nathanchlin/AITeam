class CollisionSystem:
    def __init__(self, width, height, max_objects=10, max_levels=5):
        self.width = width
        self.height = height
        self.quadtree = QuadTree(0, 0, width, height, max_objects, max_levels)
        self.collision_pairs = []
        
    def update(self, game_objects):
        """更新碰撞系统"""
        # 清空四叉树
        self.quadtree = QuadTree(0, 0, self.width, self.height, 
                                self.quadtree.capacity, self.quadtree.max_levels)
        
        # 插入所有物体到四叉树
        for obj in game_objects:
            self.quadtree.insert(obj)
            
        # 检测碰撞
        self.collision_pairs = []
        self._check_collisions(game_objects)
        
    def _check_collisions(self, game_objects):
        """检测所有碰撞"""
        for i, obj1 in enumerate(game_objects):
            # 查询可能碰撞的物体
            potential_collisions = self.quadtree.query(obj1.boundary)
            
            for obj2 in potential_collisions:
                if obj1 != obj2 and obj1.id < obj2.id:  # 避免重复检测
                    if self._check_collision(obj1, obj2):
                        self.collision_pairs.append((obj1, obj2))
                        
    def _check_collision(self, obj1, obj2):
        """检测两个物体是否碰撞"""
        # 先进行AABB检测
        if not aabb_collision(obj1.boundary, obj2.boundary):
            return False
            
        # 根据物体类型进行精确检测
        if obj1.shape == "circle" and obj2.shape == "circle":
            return circle_collision(obj1, obj2)
        elif obj1.shape == "polygon" and obj2.shape == "polygon":
            return polygon_collision(obj1, obj2)
        else:
            # 混合形状检测
            return mixed_shape_collision(obj1, obj2)
            
    def get_collisions(self):
        """获取所有碰撞对"""
        return self.collision_pairs