class EnemyFactory:
    def __init__(self):
        self.spawn_timer = 0
        self.spawn_interval = 60  # 初始生成间隔
        self.difficulty_level = 1
        self.enemies_spawned = 0
        
    def update(self):
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            return self.create_enemy()
        return None
    
    def create_enemy(self):
        self.enemies_spawned += 1
        self._adjust_difficulty()
        
        # 根据难度和已生成敌机数量决定敌机类型
        enemy_type = self._determine_enemy_type()
        
        # 随机生成位置
        x = random.randint(50, SCREEN_WIDTH - 50)
        y = -30
        
        return EnemyPlane(x, y, enemy_type)
    
    def _adjust_difficulty(self):
        # 每10秒增加难度
        if self.enemies_spawned % 10 == 0:
            self.difficulty_level += 1
            # 减少生成间隔，加快游戏节奏
            self.spawn_interval = max(20, self.spawn_interval - 5)
    
    def _determine_enemy_type(self):
        # 根据难度和随机数决定敌机类型
        rand = random.random()
        
        if self.difficulty_level < 3:
            # 简单难度，主要是基础敌机
            if rand < 0.7:
                return "basic"
            else:
                return "fast"
        elif self.difficulty_level < 6:
            # 中等难度，增加重型敌机
            if rand < 0.5:
                return "basic"
            elif rand < 0.8:
                return "fast"
            else:
                return "heavy"
        else:
            # 困难难度，增加更多敌机类型
            if rand < 0.3:
                return "basic"
            elif rand < 0.5:
                return "fast"
            elif rand < 0.7:
                return "heavy"
            elif rand < 0.9:
                return "zigzag"
            else:
                return "boss"