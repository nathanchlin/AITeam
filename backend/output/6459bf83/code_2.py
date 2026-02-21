class PhysicsEngine:
    def __init__(self, width, height):
        """
        初始化物理引擎
        
        参数:
            width, height: 游戏世界的宽度和高度
        """
        self.width = width
        self.height = height
        self.bullets = []
    
    def update(self, tanks, current_time):
        """更新物理状态"""
        # 更新所有子弹
        for bullet in self.bullets[:]:
            bullet.update()
            
            # 检查子弹是否超出边界
            if (bullet.x < 0 or bullet.x > self.width or 
                bullet.y < 0 or bullet.y > self.height):
                bullet.active = False
                self.bullets.remove(bullet)
                continue
            
            # 检查子弹与坦克的碰撞
            for tank in tanks:
                if tank != bullet.owner and self.check_collision(bullet, tank):
                    tank.health -= bullet.damage
                    bullet.active = False
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    break
    
    def check_collision(self, obj1, obj2):
        """
        检查两个对象是否碰撞
        
        参数:
            obj1, obj2: 要检查碰撞的对象，需要有get_rect()方法
        """
        rect1 = obj1.get_rect()
        rect2 = obj2.get_rect()
        return rect1.colliderect(rect2)
    
    def check_wall_collision(self, tank):
        """检查坦克与边界的碰撞"""
        tank_rect = tank.get_rect()
        
        # 左右边界
        if tank_rect.left < 0:
            tank.x = tank.width / 2
        elif tank_rect.right > self.width:
            tank.x = self.width - tank.width / 2
        
        # 上下边界
        if tank_rect.top < 0:
            tank.y = tank.height / 2
        elif tank_rect.bottom > self.height:
            tank.y = self.height - tank.height / 2