class SpaceShooterGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("太空射击游戏")
        self.clock = pygame.time.Clock()
        self.reset()
    
    def reset(self):
        """重置游戏状态"""
        self.player = Player()
        self.enemies = []
        self.bullets = []
        self.asteroids = []
        self.powerups = []
        self.score = 0
        self.difficulty = 1.0
        self.enemy_spawn_timer = 0
        self.asteroid_spawn_timer = 0
    
    def update(self):
        """更新游戏逻辑"""
        self.player.update()
        
        # 更新敌人
        for enemy in self.enemies[:]:
            enemy.update()
            if enemy.is_off_screen():
                self.enemies.remove(enemy)
        
        # 更新子弹
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.is_off_screen():
                self.bullets.remove(bullet)
        
        # 更新陨石
        for asteroid in self.asteroids[:]:
            asteroid.update()
            if asteroid.is_off_screen():
                self.asteroids.remove(asteroid)
        
        # 生成敌人
        self.enemy_spawn_timer += 1
        if self.enemy_spawn_timer > 60 / self.difficulty:
            self.spawn_enemy()
            self.enemy_spawn_timer = 0
        
        # 生成陨石
        self.asteroid_spawn_timer += 1
        if self.asteroid_spawn_timer > 120 / self.difficulty:
            self.spawn_asteroid()
            self.asteroid_spawn_timer = 0
        
        # 碰撞检测
        self.check_collisions()
    
    def spawn_enemy(self):
        """生成敌人"""
        self.enemies.append(Enemy(random.randint(0, 800), -50))
    
    def spawn_asteroid(self):
        """生成陨石"""
        self.asteroids.append(Asteroid(random.randint(0, 800), -50))
    
    def check_collisions(self):
        """检查碰撞"""
        # 子弹与敌人的碰撞
        for bullet in self.bullets[:]:
            for enemy in self.enemies[:]:
                if bullet.rect.colliderect(enemy.rect):
                    self.bullets.remove(bullet)
                    self.enemies.remove(enemy)
                    self.score += 100
                    break
        
        # 玩家与敌人的碰撞
        for enemy in self.enemies[:]:
            if self.player.rect.colliderect(enemy.rect):
                self.enemies.remove(enemy)
                self.player.take_damage()
        
        # 玩家与陨石的碰撞
        for asteroid in self.asteroids[:]:
            if self.player.rect.colliderect(asteroid.rect):
                self.asteroids.remove(asteroid)
                self.player.take_damage()
    
    def increase_difficulty(self):
        """增加游戏难度"""
        self.difficulty += 0.2
    
    def render(self):
        """渲染游戏画面"""
        self.screen.fill((0, 0, 0))  # 黑色背景
        
        # 绘制玩家
        self.player.draw(self.screen)
        
        # 绘制敌人
        for enemy in self.enemies:
            enemy.draw(self.screen)
        
        # 绘制子弹
        for bullet in self.bullets:
            bullet.draw(self.screen)
        
        # 绘制陨石
        for asteroid in self.asteroids:
            asteroid.draw(self.screen)
        
        pygame.display.flip()