class CollisionManager:
    def __init__(self):
        self.player = None
        self.enemies = []
        self.bullets = []
    
    def set_player(self, player):
        self.player = player
    
    def add_enemy(self, enemy):
        self.enemies.append(enemy)
    
    def add_bullet(self, bullet):
        self.bullets.append(bullet)
    
    def update(self):
        """更新所有碰撞检测"""
        # 玩家与敌机碰撞
        self._check_player_enemy_collisions()
        
        # 玩家与子弹碰撞
        self._check_player_bullet_collisions()
        
        # 敌机与子弹碰撞
        self._check_enemy_bullet_collisions()
    
    def _check_player_enemy_collisions(self):
        """检测玩家与敌机的碰撞"""
        if not self.player:
            return
            
        for enemy in self.enemies[:]:
            if check_collision(self.player, enemy):
                self._handle_player_enemy_collision(self.player, enemy)
    
    def _check_player_bullet_collisions(self):
        """检测玩家与子弹的碰撞"""
        if not self.player:
            return
            
        for bullet in self.bullets[:]:
            if bullet.owner_type == "enemy" and check_collision(self.player, bullet):
                self._handle_player_bullet_collision(self.player, bullet)
    
    def _check_enemy_bullet_collisions(self):
        """检测敌机与子弹的碰撞"""
        for bullet in self.bullets[:]:
            if bullet.owner_type == "player":
                for enemy in self.enemies[:]:
                    if check_collision(enemy, bullet):
                        self._handle_enemy_bullet_collision(enemy, bullet)
                        break
    
    def _handle_player_enemy_collision(self, player, enemy):
        """处理玩家与敌机碰撞"""
        player.health -= 50
        enemy.active = False
        
        if player.health <= 0:
            player.active = False
    
    def _handle_player_bullet_collision(self, player, bullet):
        """处理玩家与子弹碰撞"""
        player.health -= 20
        bullet.active = False
        
        if player.health <= 0:
            player.active = False
    
    def _handle_enemy_bullet_collision(self, enemy, bullet):
        """处理敌机与子弹碰撞"""
        enemy.health -= 25
        bullet.active = False
        
        if enemy.health <= 0:
            enemy.active = False
            self.player.score += 100