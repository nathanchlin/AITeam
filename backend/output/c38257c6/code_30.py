class BrickFactory:
    @staticmethod
    def create_brick(brick_type, x, y, width, height):
        """根据类型创建不同种类的砖块"""
        if brick_type == "normal":
            return Brick(x, y, width, height, (255, 0, 0), hits=1, points=10)
        elif brick_type == "strong":
            return Brick(x, y, width, height, (0, 0, 255), hits=2, points=20)
        elif brick_type == "super":
            return Brick(x, y, width, height, (255, 215, 0), hits=3, points=30)
        elif brick_type == "unbreakable":
            return Brick(x, y, width, height, (128, 128, 128), hits=-1, points=0)
        else:
            return Brick(x, y, width, height, (255, 0, 0), hits=1, points=10)

class BrickLayout:
    def __init__(self, rows, cols, brick_width, brick_height, spacing=5):
        self.rows = rows
        self.cols = cols
        self.brick_width = brick_width
        self.brick_height = brick_height
        self.spacing = spacing
        self.bricks = []
        
    def create_layout(self, pattern=None):
        """根据模式创建砖块布局"""
        self.bricks = []
        
        # 如果没有提供模式，则创建默认布局
        if pattern is None:
            pattern = []
            for row in range(self.rows):
                pattern_row = []
                for col in range(self.cols):
                    # 简单的模式：前两行是super，中间两行是strong，其余是normal
                    if row < 2:
                        pattern_row.append("super")
                    elif row < 4:
                        pattern_row.append("strong")
                    else:
                        pattern_row.append("normal")
                pattern.append(pattern_row)
        
        # 根据模式创建砖块
        for row in range(self.rows):
            for col in range(self.cols):
                x = col * (self.brick_width + self.spacing) + self.spacing
                y = row * (self.brick_height + self.spacing) + self.spacing + 50  # 顶部留出空间
                
                brick_type = pattern[row][col]
                brick = BrickFactory.create_brick(
                    brick_type, 
                    x, y, 
                    self.brick_width, 
                    self.brick_height
                )
                self.bricks.append(brick)
    
    def draw(self, surface):
        """绘制所有砖块"""
        for brick in self.bricks:
            brick.draw(surface)
    
    def get_active_bricks(self):
        """获取所有活跃的砖块"""
        return [brick for brick in self.bricks if brick.is_active]
    
    def is_cleared(self):
        """检查是否所有砖块都被消除"""
        return all(not brick.is_active for brick in self.bricks)