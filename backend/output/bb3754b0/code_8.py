class CollisionDetector:
    def __init__(self):
        pass
    
    def check_collision(self, bird, pipes, ground_height, game_width):
        """
        检测小鸟与所有障碍物的碰撞
        :param bird: 小鸟对象 (x, y, radius)
        :param pipes: 管道列表 [(x, top_height, bottom_y, gap_y, gap_height), ...]
        :param ground_height: 地面高度
        :param game_width: 游戏宽度
        :return: 如果发生碰撞返回True，否则返回False
        """
        bird_x, bird_y, bird_radius = bird
        
        # 检测与地面的碰撞
        if bird_y + bird_radius >= ground_height:
            return True
        
        # 检测与天花板的碰撞
        if bird_y - bird_radius <= 0:
            return True
        
        # 检测与管道的碰撞
        for pipe in pipes:
            pipe_x, top_height, bottom_y, gap_y, gap_height = pipe
            
            # 检查小鸟是否在管道的水平范围内
            if bird_x + bird_radius > pipe_x and bird_x - bird_radius < pipe_x + PIPE_WIDTH:
                # 检测与上管道的碰撞
                if bird_y - bird_radius < top_height:
                    return True
                
                # 检测与下管道的碰撞
                if bird_y + bird_radius > bottom_y:
                    return True
        
        return False
    
    def check_score(self, bird, pipes):
        """
        检测小鸟是否通过管道，用于计分
        :param bird: 小鸟对象 (x, y, radius)
        :param pipes: 管道列表 [(x, top_height, bottom_y, gap_y, gap_height, scored), ...]
        :return: 通过的管道索引列表
        """
        bird_x = bird[0]
        scored_pipes = []
        
        for i, pipe in enumerate(pipes):
            pipe_x, top_height, bottom_y, gap_y, gap_height, scored = pipe
            
            # 如果小鸟已经通过管道且尚未计分
            if bird_x > pipe_x + PIPE_WIDTH and not scored:
                scored_pipes.append(i)
        
        return scored_pipes