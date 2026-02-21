class Ninja:
    def __init__(self):
        self.position = Vector2(0, 0)
        self.velocity = Vector2(0, 0)
        self.is_jumping = False
        self.is_sliding = False
        self.health = 100
        self.speed = 5
        self.jump_power = 15
        self.gravity = 0.8
        
    def jump(self):
        if not self.is_jumping:
            self.velocity.y = -self.jump_power
            self.is_jumping = True
            
    def slide(self):
        if not self.is_sliding and not self.is_jumping:
            self.is_sliding = True
            # 降低碰撞箱高度
            
    def update(self):
        # 应用重力
        self.velocity.y += self.gravity
        
        # 更新位置
        self.position += self.velocity
        
        # 地面检测
        if self.position.y >= GROUND_HEIGHT:
            self.position.y = GROUND_HEIGHT
            self.velocity.y = 0
            self.is_jumping = False
            self.is_sliding = False