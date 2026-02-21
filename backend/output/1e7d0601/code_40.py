class OptimizedCollisionManager(CollisionManager):
    def __init__(self):
        super().__init__()
        self.spatial_hash = {}
        self.cell_size = 50  # 空间哈希单元大小
    
    def _get_cell_key(self, obj):
        """获取对象的空间哈希键"""
        x = int(obj.x / self.cell_size)
        y = int(obj.y / self.cell_size)
        return (x, y)
    
    def _update_spatial_hash(self):
        """更新空间哈希表"""
        self.spatial_hash.clear()
        
        # 添加玩家
        if self.player and self.player.active:
            key = self._get_cell_key(self.player)
            if key not in self.spatial_hash:
                self.spatial_hash[key] = []
            self.spatial_hash[key].append(self.player)
        
        # 添加敌机
        for enemy in self.enemies:
            if enemy.active:
                key = self._get_cell_key(enemy)
                if key not in self.spatial_hash:
                    self.spatial_hash[key] = []
                self.spatial_hash[key].append(enemy)
        
        # 添加子弹
        for bullet in self.bullets:
            if bullet.active:
                key = self._get_cell_key(bullet)
                if key not in self.spatial_hash:
                    self.spatial_hash[key] = []
                self.spatial_hash[key].append(bullet)
    
    def _get_nearby_objects(self, obj):
        """获取附近的对象用于碰撞检测"""
        key = self._get_cell_key(obj)
        nearby = []
        
        # 检查当前单元和相邻的8个单元
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nearby_key = (key[0] + dx, key[1] + dy)
                if nearby_key in self.spatial_hash:
                    nearby.extend(self.spatial_hash[nearby_key])
        
        return nearby
    
    def update(self):
        """更新所有碰撞检测（优化版）"""
        self._update_spatial_hash()
        
        # 玩家与敌机碰撞
        if self.player and self.player.active:
            nearby_objects = self._get_nearby_objects(self.player)
            for obj in nearby_objects:
                if isinstance(obj, Enemy) and check_collision(self.player, obj):
                    self._handle_player_enemy_collision(self.player, obj)
        
        # 玩家与子弹碰撞
        if self.player and self.player.active:
            nearby_objects = self._get_nearby_objects(self.player)
            for obj in nearby_objects:
                if isinstance(obj, Bullet) and obj.owner_type == "enemy" and check_collision(self.player, obj):
                    self._handle_player_bullet_collision(self.player, obj)
        
        # 敌机与子弹碰撞
        for bullet in self.bullets[:]:
            if bullet.active and bullet.owner_type == "player":
                nearby_objects = self._get_nearby_objects(bullet)
                for obj in nearby_objects:
                    if isinstance(obj, Enemy) and check_collision(obj, bullet):
                        self._handle_enemy_bullet_collision(obj, bullet)
                        break