class Obstacle:
    def __init__(self, position, obstacle_type):
        self.position = position
        self.type = obstacle_type  # "ground", "air", "slide"
        self.width = OBSTACLE_WIDTH
        self.height = OBSTACLE_HEIGHT
        self.passed = False
        self.active = True
    
    def update(self, delta_time, game_speed):
        """更新障碍物位置"""
        self.position.x -= game_speed * delta_time
        if self.position.x + self.width < 0:
            self.active = False
    
    def get_collision_box(self):
        """获取碰撞框"""
        return Box(self.position, Vector2(self.width, self.height))