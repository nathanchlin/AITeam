class CollisionDetector:
    def __init__(self, game_width, game_height):
        """
        初始化碰撞检测器
        
        参数:
            game_width: 游戏区域的宽度(格子数)
            game_height: 游戏区域的高度(格子数)
        """
        self.game_width = game_width
        self.game_height = game_height
    
    def check_wall_collision(self, snake_head):
        """
        检测是否撞墙
        
        参数:
            snake_head: 蛇头的坐标 (x, y)
            
        返回:
            bool: 如果撞墙返回True，否则返回False
        """
        x, y = snake_head
        # 检查是否超出边界
        if x < 0 or x >= self.game_width or y < 0 or y >= self.game_height:
            return True
        return False
    
    def check_self_collision(self, snake_head, snake_body):
        """
        检测是否撞到自身
        
        参数:
            snake_head: 蛇头的坐标 (x, y)
            snake_body: 蛇身的坐标列表，不包括蛇头
            
        返回:
            bool: 如果撞到自身返回True，否则返回False
        """
        # 将蛇头坐标与蛇身所有部分比较
        for segment in snake_body:
            if snake_head == segment:
                return True
        return False
    
    def check_collision(self, snake_head, snake_body):
        """
        综合碰撞检测，检查撞墙和撞自身
        
        参数:
            snake_head: 蛇头的坐标 (x, y)
            snake_body: 蛇身的坐标列表，不包括蛇头
            
        返回:
            bool: 如果发生碰撞返回True，否则返回False
        """
        # 检查是否撞墙
        if self.check_wall_collision(snake_head):
            return True
        
        # 检查是否撞自身
        if self.check_self_collision(snake_head, snake_body):
            return True
        
        return False