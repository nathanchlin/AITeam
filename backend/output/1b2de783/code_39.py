class CollisionGroups:
    def __init__(self):
        self.groups = {
            "player": set(),
            "enemy": set(),
            "bullet": set(),
            "asteroid": set()
        }
        
    def add_object(self, obj, group):
        """添加物体到碰撞组"""
        if group in self.groups:
            self.groups[group].add(obj)
            
    def get_potential_collisions(self, group1, group2):
        """获取两个组之间可能碰撞的物体对"""
        if group1 in self.groups and group2 in self.groups:
            return [(a, b) for a in self.groups[group1] 
                    for b in self.groups[group2]]
        return []