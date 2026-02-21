class ObstacleGenerator:
    def __init__(self):
        self.obstacles = []
        self.spawn_timer = 0
        self.spawn_interval = INITIAL_SPAWN_INTERVAL
        self.patterns = self._generate_patterns()
    
    def _generate_patterns(self):
        """生成障碍物模式"""
        return [
            {"type": "ground", "count": 1, "gap": 300},
            {"type": "air", "count": 1, "gap": 400},
            {"type": "slide", "count": 1, "gap": 500},
            {"type": "mixed", "count": 3, "gap": 200}
        ]
    
    def update(self, delta_time, game_speed):
        """更新障碍物生成器"""
        self.spawn_timer += delta_time
        
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            # 随机选择一个模式
            pattern = random.choice(self.patterns)
            self._spawn_pattern(pattern)
            
            # 随着游戏进行，增加生成难度
            self.spawn_interval = max(MIN_SPAWN_INTERVAL, self.spawn_interval - 0.01)
    
    def _spawn_pattern(self, pattern):
        """根据模式生成障碍物"""
        if pattern["type"] == "ground":
            self.obstacles.append(Obstacle(
                Vector2(SCREEN_WIDTH, GROUND_LEVEL),
                "ground"
            ))
        elif pattern["type"] == "air":
            self.obstacles.append(Obstacle(
                Vector2(SCREEN_WIDTH, GROUND_LEVEL - 150),
                "air"
            ))
        elif pattern["type"] == "slide":
            self.obstacles.append(Obstacle(
                Vector2(SCREEN_WIDTH, GROUND_LEVEL),
                "slide"
            ))
        elif pattern["type"] == "mixed":
            for i in range(pattern["count"]):
                obstacle_type = random.choice(["ground", "air"])
                self.obstacles.append(Obstacle(
                    Vector2(SCREEN_WIDTH + i * pattern["gap"], GROUND_LEVEL if obstacle_type == "ground" else GROUND_LEVEL - 150),
                    obstacle_type
                ))
    
    def get_active_obstacles(self):
        """获取所有活动障碍物"""
        return [obs for obs in self.obstacles if obs.active]
    
    def remove_inactive_obstacles(self):
        """移除非活动障碍物"""
        self.obstacles = [obs for obs in self.obstacles if obs.active]