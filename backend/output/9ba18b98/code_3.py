class Tetromino:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.shape_index = random.randint(0, len(SHAPES) - 1)
        self.shape = SHAPES[self.shape_index]
        self.color = COLORS[self.shape_index]
        self.rotation = 0
    
    def get_shape(self):
        """获取当前旋转状态的方块形状"""
        return self.shape
    
    def get_color(self):
        """获取方块颜色"""
        return self.color
    
    def move(self, dx, dy):
        """移动方块"""
        self.x += dx
        self.y += dy
    
    def rotate(self):
        """旋转方块"""
        # 简单的顺时针旋转
        rotated = [[self.shape[y][x] for y in range(len(self.shape)-1, -1, -1)] 
                  for x in range(len(self.shape[0]))]
        self.shape = rotated