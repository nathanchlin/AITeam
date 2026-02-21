class EnemyPlane:
    def __init__(self, x, y, enemy_type="basic"):
        self.x = x
        self.y = y
        self.enemy_type = enemy_type
        self.health = self._get_health_by_type()
        self.speed = self._get_speed_by_type()
        self.score_value = self._get_score_by_type()
        self.shoot_cooldown = 0
        self.active = True
        self.path_index = 0
        self.movement_pattern = self._get_movement_pattern()
        
    def _get_health_by_type(self):
        health_map = {
            "basic": 1,
            "fast": 1,
            "heavy": 3,
            "zigzag": 1,
            "boss": 10
        }
        return health_map.get(self.enemy_type, 1)
    
    def _get_speed_by_type(self):
        speed_map = {
            "basic": 2,
            "fast": 4,
            "heavy": 1,
            "zigzag": 2,
            "boss": 1.5
        }
        return speed_map.get(self.enemy_type, 2)
    
    def _get_score_by_type(self):
        score_map = {
            "basic": 100,
            "fast": 150,
            "heavy": 300,
            "zigzag": 200,
            "boss": 1000
        }
        return score_map.get(self.enemy_type, 100)
    
    def _get_movement_pattern(self):
        patterns = {
            "basic": "straight",
            "fast": "straight",
            "heavy": "straight",
            "zigzag": "zigzag",
            "boss": "circle"
        }
        return patterns.get(self.enemy_type, "straight")
    
    def update(self):
        if not self.active:
            return
            
        # 更新位置
        self._move()
        
        # 更新射击冷却
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
            
        # 检查是否超出屏幕
        if self.y > SCREEN_HEIGHT + 50:
            self.active = False
    
    def _move(self):
        if self.movement_pattern == "straight":
            self.y += self.speed
        elif self.movement_pattern == "zigzag":
            self.y += self.speed
            self.x += math.sin(self.y * 0.05) * 2
        elif self.movement_pattern == "circle":
            angle = self.path_index * 0.05
            radius = 100
            self.x += math.cos(angle) * self.speed * 0.5
            self.y += self.speed + math.sin(angle) * self.speed * 0.5
            self.path_index += 1
    
    def take_damage(self, damage=1):
        self.health -= damage
        if self.health <= 0:
            self.active = False
            return True  # 返回True表示敌机被摧毁
        return False
    
    def can_shoot(self):
        return self.shoot_cooldown <= 0
    
    def shoot(self):
        if self.can_shoot():
            self.shoot_cooldown = self._get_shoot_cooldown_by_type()
            return Bullet(self.x, self.y + 20, 5, "enemy")
        return None
    
    def _get_shoot_cooldown_by_type(self):
        cooldown_map = {
            "basic": 60,
            "fast": 40,
            "heavy": 90,
            "zigzag": 50,
            "boss": 30
        }
        return cooldown_map.get(self.enemy_type, 60)