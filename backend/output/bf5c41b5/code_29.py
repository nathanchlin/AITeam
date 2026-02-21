class BrickCollisionHandler:
    def __init__(self, brick_generator: BrickGenerator):
        self.brick_generator = brick_generator
        
    def check_collision(self, ball_rect: pygame.Rect) -> List[Brick]:
        """检查球与砖块的碰撞，返回碰撞的砖块列表"""
        collided_bricks = []
        bricks = self.brick_generator.get_bricks()
        
        for brick in bricks:
            if not brick.is_destroyed and ball_rect.colliderect(brick.rect):
                collided_bricks.append(brick)
                
        return collided_bricks
    
    def handle_collisions(self, ball_rect: pygame.Rect, ball_speed: Tuple[int, int]) -> Tuple[List[Brick], bool]:
        """处理碰撞，返回被消除的砖块列表和是否发生爆炸"""
        collided_bricks = self.check_collision(ball_rect)
        eliminated_bricks = []
        explosion_occurred = False
        
        for brick in collided_bricks:
            if brick.hit():
                eliminated_bricks.append(brick)
                
                # 处理特殊砖块效果
                if brick.type == BrickType.EXPLOSIVE:
                    explosion_occurred = True
                    self._handle_explosion(brick)
                elif brick.type == BrickType.BONUS:
                    self._handle_bonus(brick)
        
        # 移除已销毁的砖块
        self.brick_generator.remove_destroyed_bricks()
        
        return eliminated_bricks, explosion_occurred
    
    def _handle_explosion(self, explosive_brick: Brick):
        """处理爆炸砖块效果，消除周围砖块"""
        bricks = self.brick_generator.get_bricks()
        explosion_radius = 1  # 爆炸影响周围1格的砖块
        
        for brick in bricks:
            if brick == explosive_brick or brick.is_destroyed:
                continue
                
            # 检查是否在爆炸范围内
            distance_x = abs(brick.rect.centerx - explosive_brick.rect.centerx)
            distance_y = abs(brick.rect.centery - explosive_brick.rect.centery)
            
            if (distance_x <= (explosive_brick.rect.width + brick.rect.width) * explosion_radius / 2 and
                distance_y <= (explosive_brick.rect.height + brick.rect.height) * explosion_radius / 2):
                brick.hit()
    
    def _handle_bonus(self, bonus_brick: Brick):
        """处理奖励砖块效果"""
        # 这里可以添加特殊效果，如扩大挡板、多球等
        # 目前只做简单标记
        bonus_brect.is_destroyed = True