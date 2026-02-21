class QuadTree:
    def __init__(self, boundary, capacity):
        self.boundary = boundary  # 边界矩形
        self.capacity = capacity  # 节点容量
        self.objects = []
        self.divided = False
        self.northeast = None
        self.northwest = None
        self.southeast = None
        self.southwest = None
    
    def insert(self, obj):
        if not self.boundary.contains(obj):
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
        if found is None:
            found = []
        
        if not self.boundary.intersects(range):
            return found
        
        for obj in self.objects:
            if range.contains(obj):
                found.append(obj)
        
        if self.divided:
            self.northeast.query(range, found)
            self.northwest.query(range, found)
            self.southeast.query(range, found)
            self.southwest.query(range, found)
        
        return found