class BrickGenerator:
    def __init__(self, screen_width: int, screen_height: int, brick_width: int, brick_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.brick_width = brick_width
        self.brick_height = brick_height
        self.bricks: List[Brick] = []
        
    def generate_level(self, level: int):
        """根据关卡生成砖块布局"""
        self.bricks.clear()
        
        # 计算每行砖块数量和行数
        bricks_per_row = (self.screen_width - 100) // self.brick_width
        rows = min(5 + level // 2, 10)  # 随关卡增加行数，最多10行
        
        # 计算起始位置使砖块居中
        total_width = bricks_per_row * self.brick_width
        start_x = (self.screen_width - total_width) // 2
        start_y = 50
        
        for row in range(rows):
            for col in range(bricks_per_row):
                x = start_x + col * self.brick_width
                y = start_y + row * self.brick_height
                
                # 根据关卡和位置决定砖块类型
                brick_type = self._determine_brick_type(row, col, level)
                
                brick = Brick(x, y, self.brick_width - 2, self.brick_height - 2, brick_type)
                self.bricks.append(brick)
    
    def _determine_brick_type(self, row: int, col: int, level: int) -> BrickType:
        """根据位置和关卡确定砖块类型"""
        # 前几行通常是普通砖块
        if row < 2:
            return BrickType.NORMAL
        
        # 根据关卡增加特殊砖块概率
        rand = (row + col + level) % 10
        
        if level >= 3 and rand == 0:
            return BrickType.UNBREAKABLE
        elif level >= 2 and rand == 1:
            return BrickType.HARD
        elif level >= 4 and rand == 2:
            return BrickType.EXPLOSIVE
        elif level >= 5 and rand == 3:
            return BrickType.BONUS
        else:
            return BrickType.NORMAL
    
    def get_bricks(self) -> List[Brick]:
        """获取所有砖块"""
        return self.bricks
    
    def remove_destroyed_bricks(self):
        """移除已销毁的砖块"""
        self.bricks = [brick for brick in self.bricks if not brick.is_destroyed]