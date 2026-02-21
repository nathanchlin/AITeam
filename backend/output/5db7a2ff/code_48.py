class SimplifiedPhysics:
    def __init__(self, obj):
        self.obj = obj
        self.use_full_physics = True
        self.last_update_time = 0
    
    def update(self, dt):
        # 如果物体离相机很远，使用简化物理
        if not self.use_full_physics:
            # 只更新位置，不考虑旋转和复杂碰撞
            self.obj.position += self.obj.velocity * dt
            return
        
        # 完整物理更新
        self.update_full_physics(dt)
    
    def update_full_physics(self, dt):
        # 实现完整的物理更新逻辑
        pass
    
    def set_simplified(self, is_simplified):
        self.use_full_physics = not is_simplified