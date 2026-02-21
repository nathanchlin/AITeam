class TetrominoQueue:
    def __init__(self):
        self.queue = []
        self.max_queue_size = 5
        self.bag_system = True  # 使用bag系统确保公平性
    
    def generate_bag(self):
        """生成一个包含所有7种方块的bag"""
        return random.sample(list(TETROMINO_TYPES), 7)
    
    def get_next_tetromino(self):
        """获取下一个方块"""
        if len(self.queue) < self.max_queue_size:
            if self.bag_system and len(self.queue) == 0:
                self.queue = self.generate_bag()
            else:
                self.queue.append(random.choice(list(TETROMINO_TYPES)))
        return self.queue.pop(0)