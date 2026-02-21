class CollisionDetector:
    @staticmethod
    def check_ball_brick_collision(ball, brick):
        """检测球与砖块的碰撞"""
        if not brick.is_active:
            return False
            
        ball_rect = pygame.Rect(ball.x - ball.radius, ball.y - ball.radius, 
                               ball.radius * 2, ball.radius * 2)
        brick_rect = brick.get_rect()
        
        if ball_rect.colliderect(brick_rect):
            # 确定碰撞方向
            # 计算球中心与砖块各边的距离
            ball_center_x = ball.x
            ball_center_y = ball.y
            
            # 找出最近的边
            left_dist = abs(ball_center_x - brick_rect.left)
            right_dist = abs(ball_center_x - brick_rect.right)
            top_dist = abs(ball_center_y - brick_rect.top)
            bottom_dist = abs(ball_center_y - brick_rect.bottom)
            
            min_dist = min(left_dist, right_dist, top_dist, bottom_dist)
            
            # 根据碰撞方向改变球的运动方向
            if min_dist == left_dist or min_dist == right_dist:
                ball.dx = -ball.dx
            else:
                ball.dy = -ball.dy
                
            return True
        return False