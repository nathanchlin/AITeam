class GameBoard:
    """游戏板类"""
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[0 for _ in range(width)] for _ in range(height)]
        self.current_piece = None
        self.next_piece = None
        
    def reset(self):
        """重置游戏板"""
        self.grid = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.current_piece = None
        self.next_piece = None
        
    def check_top_reached(self):
        """检查是否有方块堆积到顶部"""
        # 检查顶部两行是否有任何方块
        for row in range(2):
            for col in range(self.width):
                if self.grid[row][col] != 0:
                    return True
        return False
        
    def check_line_clear(self):
        """检查并清除完整的行"""
        lines_to_clear = []
        for row in range(self.height):
            if all(self.grid[row]):
                lines_to_clear.append(row)
                
        # 清除完整的行
        for row in lines_to_clear:
            del self.grid[row]
            self.grid.insert(0, [0 for _ in range(self.width)])
            
        return len(lines_to_clear)