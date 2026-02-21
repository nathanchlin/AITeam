class Character:
    def __init__(self):
        self.position = Vector2(0, 0)
        self.velocity = Vector2(0, 0)
        self.acceleration = Vector2(0, 0)
        self.is_jumping = False
        self.is_sliding = False
        self.animation_state = "idle"
        self.health = 100
        self.score = 0
    
    def jump(self):
        """跳跃动作"""
        if not self.is_jumping:
            self.velocity.y = JUMP_FORCE
            self.is_jumping = True
            self.animation_state = "jump"
    
    def slide(self):
        """滑铲动作"""
        if not self.is_sliding and self.is_jumping:
            self.is_sliding = True
            self.animation_state = "slide"
    
    def update(self, delta_time):
        """更新角色状态"""
        # 应用重力
        self.acceleration.y = GRAVITY
        
        # 更新速度和位置
        self.velocity += self.acceleration * delta_time
        self.position += self.velocity * delta_time
        
        # 地面检测
        if self.position.y <= GROUND_LEVEL:
            self.position.y = GROUND_LEVEL
            self.velocity.y = 0
            self.is_jumping = False
            if self.is_sliding:
                self.is_sliding = False
                self.animation_state = "run"
            else:
                self.animation_state = "run"