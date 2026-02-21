class QuadTree:
    def __init__(self, boundary, capacity):
        self.boundary = boundary  # 边界矩形 (x, y, width, height)
        self.capacity = capacity  # 节点容量
        self.objects = []         # 存储的对象
        self.divided = False      # 是否已分割
        
    def insert(self, obj):
        """插入对象到四叉树"""
        if not self.contains(obj):
            return False
            
        if len(self.objects) < self.capacity:
            self.objects.append(obj)
            return True
            
        if not self.divided:
            self.subdivide()
            
        return (self.northeast.insert(obj) or 
                self.northwest.insert(obj) or 
                self.southeast.insert(obj) or 
                self.southwest.insert(obj))
    
    def query(self, range, found=None):
        """查询指定范围内的所有对象"""
        if found is None:
            found = []
            
        if not self.intersects(range):
            return found
            
        for obj in self.objects:
            if self.range_contains(range, obj):
                found.append(obj)
                
        if self.divided:
            self.northeast.query(range, found)
            self.northwest.query(range, found)
            self.southeast.query(range, found)
            self.southwest.query(range, found)
            
        return found