class ObstacleGenerator:
    def __init__(self):
        self.obstacles = []
        self.spawn_timer = 0
        self.spawn_interval = 120  # 初始生成间隔（帧数）
        self.difficulty_level = 1
        
    def update(self):
        self.spawn_timer += 1
        
        # 根据游戏进度调整难度
        if self.spawn_timer % 600 == 0:  # 每10秒增加难度
            self.difficulty_level += 1
            self.spawn_interval = max(30, self.spawn_interval - 5)
        
        # 生成新障碍物
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_obstacle()
            self.spawn_timer = 0
            
        # 更新所有障碍物
        for obstacle in self.obstacles[:]:
            obstacle.update()
            if obstacle.is_off_screen():
                self.obstacles.remove(obstacle)
                
    def spawn_obstacle(self):
        # 根据难度选择障碍物类型
        if self.difficulty_level < 3:
            obstacle_type = random.choice(['ground', 'air'])
        else:
            obstacle_type = random.choice(['ground', 'air', 'projectile'])
            
        obstacle = Obstacle(obstacle_type, self.difficulty_level)
        self.obstacles.append(obstacle)