class EnemySpawner:
    def __init__(self, game_settings):
        self.game_settings = game_settings
        self.spawn_timer = 0
        self.difficulty_level = 1
        self.enemies_to_spawn = []
        self.boss_spawned = False
        
    def update(self, player, enemies, game_state):
        # 根据分数调整难度
        self.difficulty_level = 1 + player.score // 100
        
        # 更新生成计时器
        self.spawn_timer += 1
        
        # 根据难度调整生成间隔
        spawn_interval = max(30, 120 - self.difficulty_level * 5)
        
        # 生成敌人
        if self.spawn_timer >= spawn_interval:
            self.spawn_timer = 0
            self._decide_spawn(player, enemies, game_state)
    
    def _decide_spawn(self, player, enemies, game_state):
        # 根据游戏状态决定生成什么敌人
        if not self.boss_spawned and player.score >= 500 and len(enemies) < 3:
            # 生成Boss
            self._spawn_boss(player)
            self.boss_spawned = True
        else:
            # 根据难度和随机性决定生成普通敌人
            spawn_roll = random.random()
            
            # 根据难度增加高级敌人的概率
            elite_chance = min(0.2, self.difficulty_level * 0.02)
            heavy_chance = min(0.3, self.difficulty_level * 0.03)
            fast_chance = min(0.4, self.difficulty_level * 0.04)
            
            if spawn_roll < elite_chance:
                self._spawn_elite(player)
            elif spawn_roll < elite_chance + heavy_chance:
                self._spawn_heavy(player)
            elif spawn_roll < elite_chance + heavy_chance + fast_chance:
                self._spawn_fast(player)
            else:
                self._spawn_basic(player)
    
    def _spawn_basic(self, player):
        # 在屏幕上方随机位置生成基础敌人
        x = random.randint(50, self.game_settings["screen_width"] - 50)
        y = -30
        enemy = Enemy(x, y, EnemyType.BASIC, self.game_settings)
        self.enemies_to_spawn.append(enemy)
    
    def _spawn_fast(self, player):
        # 在屏幕上方随机位置生成快速敌人
        x = random.randint(50, self.game_settings["screen_width"] - 50)
        y = -30
        enemy = Enemy(x, y, EnemyType.FAST, self.game_settings)
        self.enemies_to_spawn.append(enemy)
    
    def _spawn_heavy(self, player):
        # 在屏幕上方随机位置生成重型敌人
        x = random.randint(50, self.game_settings["screen_width"] - 50)
        y = -30
        enemy = Enemy(x, y, EnemyType.HEAVY, self.game_settings)
        self.enemies_to_spawn.append(enemy)
    
    def _spawn_elite(self, player):
        # 在屏幕上方随机位置生成精英敌人
        x = random.randint(50, self.game_settings["screen_width"] - 50)
        y = -30
        enemy = Enemy(x, y, EnemyType.ELITE, self.game_settings)
        self.enemies_to_spawn.append(enemy)
    
    def _spawn_boss(self, player):
        # 在屏幕上方中间位置生成Boss
        x = self.game_settings["screen_width"] // 2
        y = -100
        enemy = Enemy(x, y, EnemyType.BOSS, self.game_settings)
        self.enemies_to_spawn.append(enemy)
    
    def get_enemies_to_spawn(self):
        return self.enemies_to_spawn
    
    def clear_spawned_enemies(self):
        self.enemies_to_spawn = []