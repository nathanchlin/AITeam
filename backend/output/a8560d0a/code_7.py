class SpatialGrid:
    def __init__(self, cell_size):
        self.cell_size = cell_size
        self.grid = {}
    
    def add_object(self, obj):
        cell_x = int(obj.position.x / self.cell_size)
        cell_y = int(obj.position.y / self.cell_size)
        cell_key = (cell_x, cell_y)
        
        if cell_key not in self.grid:
            self.grid[cell_key] = []
        self.grid[cell_key].append(obj)
    
    def get_nearby_objects(self, obj, radius):
        cell_x = int(obj.position.x / self.cell_size)
        cell_y = int(obj.position.y / self.cell_size)
        
        nearby_objects = []
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                cell_key = (cell_x + dx, cell_y + dy)
                if cell_key in self.grid:
                    nearby_objects.extend(self.grid[cell_key])
        
        return nearby_objects