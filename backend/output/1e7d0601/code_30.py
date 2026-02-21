class EnemyFormation:
    def __init__(self):
        self.formation_types = ["line", "v_shape", "diamond", "circle"]
        self.current_formation = "line"
        self.formation_timer = 0
        self.formation_interval = 300  # 每5秒变换一次队形
        
    def update(self):
        self.formation_timer += 1
        if self.formation_timer >= self.formation_interval:
            self.formation_timer = 0
            self.current_formation = random.choice(self.formation_types)
            
    def get_spawn_position(self, index, total_enemies):
        if self.current_formation == "line":
            # 水平线队形
            x = (SCREEN_WIDTH / (total_enemies + 1)) * (index + 1)
            y = -50
        elif self.current_formation == "v_shape":
            # V字队形
            if index < total_enemies / 2:
                x = SCREEN_WIDTH / 2 - (index * 60)
            else:
                x = SCREEN_WIDTH / 2 + ((index - total_enemies / 2) * 60)
            y = -50 - abs(index - total_enemies / 2) * 10
        elif self.current_formation == "diamond":
            # 钻石队形
            if index < total_enemies / 2:
                x = SCREEN_WIDTH / 2 + (index * 40) - (total_enemies / 2 * 40)
                y = -50 - index * 15
            else:
                x = SCREEN_WIDTH / 2 + ((total_enemies - index - 1) * 40) - (total_enemies / 2 * 40)
                y = -50 - (total_enemies - index - 1) * 15
        else:  # circle
            # 圆形队形
            angle = (2 * math.pi / total_enemies) * index
            radius = 100
            x = SCREEN_WIDTH / 2 + math.cos(angle) * radius
            y = -50 + math.sin(angle) * radius
            
        return x, y