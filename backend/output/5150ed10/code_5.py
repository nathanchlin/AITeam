class CollisionDetector:
    @staticmethod
    def check_collision(player_rect, obstacles):
        """
        检测玩家与障碍物的碰撞
        返回: (是否碰撞, 碰撞的障碍物类型)
        """
        for obstacle in obstacles:
            if player_rect.colliderect(obstacle.rect):
                return True, obstacle.type
        return False, None
    
    @staticmethod
    def check_pixel_perfect_collision(player_surface, player_rect, obstacle_surface, obstacle_rect):
        """
        像素级精确碰撞检测（适用于有透明区域的图像）
        返回: 是否碰撞
        """
        # 计算两个矩形相交的区域
        intersection = player_rect.clip(obstacle_rect)
        
        if intersection.width == 0 or intersection.height == 0:
            return False
        
        # 获取相交区域的像素数据
        player_pixels = pygame.PixelArray(player_surface)
        obstacle_pixels = pygame.PixelArray(obstacle_surface)
        
        # 检查相交区域内的像素
        for x in range(intersection.width):
            for y in range(intersection.height):
                player_pos = (x + intersection.x - player_rect.x, y + intersection.y - player_rect.y)
                obstacle_pos = (x + intersection.x - obstacle_rect.x, y + intersection.y - obstacle_rect.y)
                
                # 检查像素是否都不透明
                if (player_surface.get_at(player_pos)[3] > 0 and 
                    obstacle_surface.get_at(obstacle_pos)[3] > 0):
                    return True
        
        return False