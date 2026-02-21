class AsteroidManager:
    def __init__(self, width, height):
        """
        初始化陨石管理器
        :param width: 游戏区域宽度
        :param height: 游戏区域高度
        """
        self.width = width
        self.height = height
        self.asteroids = []
        self.spawn_timer = 0
        self.spawn_delay = 120  # 初始生成延迟（帧数）
        self.min_spawn_delay = 30  # 最小生成延迟
        self.difficulty_increase_rate = 0.99  # 难度增加速率
        
    def update(self):
        """更新所有陨石并管理生成"""
        # 更新所有陨石
        for asteroid in self.asteroids[:]:
            asteroid.update()
            
            # 移除离开屏幕的陨石
            if (asteroid.x < -asteroid.radius * 2 or 
                asteroid.x > self.width + asteroid.radius * 2 or
                asteroid.y < -asteroid.radius * 2 or 
                asteroid.y > self.height + asteroid.radius * 2):
                self.asteroids.remove(asteroid)
        
        # 生成新陨石
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_delay:
            self.spawn_asteroid()
            self.spawn_timer = 0
            # 逐渐增加难度
            self.spawn_delay = max(self.min_spawn_delay, int(self.spawn_delay * self.difficulty_increase_rate))
    
    def spawn_asteroid(self):
        """生成新陨石"""
        # 随机决定从屏幕哪边生成
        side = random.randint(0, 3)  # 0=上, 1=右, 2=下, 3=左
        
        if side == 0:  # 上边
            x = random.randint(0, self.width)
            y = -50
        elif side == 1:  # 右边
            x = self.width + 50
            y = random.randint(0, self.height)
        elif side == 2:  # 下边
            x = random.randint(0, self.width)
            y = self.height + 50
        else:  # 左边
            x = -50
            y = random.randint(0, self.height)
        
        # 随机大小，小陨石概率更高
        size_weights = [0.5, 0.35, 0.15]  # 小、中、大的概率
        size = random.choices([1, 2, 3], weights=size_weights)[0]
        
        asteroid = Asteroid(x, y, size)
        self.asteroids.append(asteroid)
    
    def draw(self, screen):
        """绘制所有陨石"""
        for asteroid in self.asteroids:
            asteroid.draw(screen)
    
    def check_collision(self, rect):
        """检查与给定矩形的碰撞"""
        for asteroid in self.asteroids[:]:
            if rect.colliderect(asteroid.get_rect()):
                # 碰撞发生，移除陨石并返回它
                self.asteroids.remove(asteroid)
                return asteroid
        return None
    
    def split_asteroid(self, asteroid):
        """分裂陨石并更新列表"""
        if asteroid in self.asteroids:
            self.asteroids.remove(asteroid)
            new_asteroids = asteroid.split()
            self.asteroids.extend(new_asteroids)
            return new_asteroids
        return []
    
    def get_all_asteroids(self):
        """获取所有陨石"""
        return self.asteroids
    
    def clear(self):
        """清除所有陨石"""
        self.asteroids = []
        self.spawn_timer = 0
        self.spawn_delay = 120