class CollisionSystem:
    def __init__(self):
        self.spatial_hash = SpatialHash()  # 空间哈希优化
        
    def update(self, ninja, obstacles):
        # 更新空间哈希
        self.spatial_hash.clear()
        for obstacle in obstacles:
            self.spatial_hash.insert(obstacle)
            
        # 获取潜在碰撞对象
        potential_collisions = self.spatial_hash.query(ninja)
        
        # 检测实际碰撞
        for obstacle in potential_collisions:
            if self.check_collision(ninja, obstacle):
                self.handle_collision(ninja, obstacle)
                
    def check_collision(self, ninja, obstacle):
        # 使用AABB碰撞检测
        ninja_rect = ninja.get_collision_rect()
        obstacle_rect = obstacle.get_collision_rect()
        
        return ninja_rect.colliderect(obstacle_rect)
        
    def handle_collision(self, ninja, obstacle):
        if obstacle.damage > 0:
            ninja.take_damage(obstacle.damage)
            
        if obstacle.type == 'ground':
            if ninja.is_sliding:
                # 滑行状态可以穿越某些地面障碍物
                pass
            else:
                # 正常碰撞处理
                pass
        elif obstacle.type == 'air':
            # 空中障碍物碰撞处理
            pass