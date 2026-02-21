class PhysicsSystem:
    @staticmethod
    def check_collision(obj1_rect, obj2_rect):
        """基本矩形碰撞检测"""
        return obj1_rect.colliderect(obj2_rect)
    
    @staticmethod
    def check_circle_collision(x1, y1, r1, x2, y2, r2):
        """圆形碰撞检测"""
        distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        return distance < (r1 + r2)
    
    @staticmethod
    def resolve_collision(obj1, obj2):
        """简单碰撞响应（弹性碰撞）"""
        # 计算碰撞角度
        dx = obj2.x - obj1.x
        dy = obj2.y - obj1.y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance == 0:  # 避免除以零
            distance = 0.01
            dx = 0.01
        
        # 归一化碰撞向量
        nx = dx / distance
        ny = dy / distance
        
        # 计算相对速度
        dvx = obj2.dx - obj1.dx
        dvy = obj2.dy - obj1.dy
        
        # 计算相对速度在碰撞法线方向的分量
        dvn = dvx * nx + dvy * ny
        
        # 如果物体正在分离，不处理
        if dvn > 0:
            return
        
        # 计算碰撞冲量
        impulse = 2 * dvn / 2  # 假设质量相等
        
        # 应用冲量
        obj1.dx += impulse * nx
        obj1.dy += impulse * ny
        obj2.dx -= impulse * nx
        obj2.dy -= impulse * ny