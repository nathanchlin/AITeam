class PipeManager:
    def __init__(self, screen_width, screen_height, pipe_gap=150, pipe_width=80, 
                 pipe_speed=5, spawn_interval=1500):
        """
        初始化管道管理器
        
        参数:
            screen_width: 屏幕宽度
            screen_height: 屏幕高度
            pipe_gap: 管道间隙大小
            pipe_width: 管道宽度
            pipe_speed: 管道移动速度
            spawn_interval: 管道生成间隔(毫秒)
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.pipe_gap = pipe_gap
        self.pipe_width = pipe_width
        self.pipe_speed = pipe_speed
        self.spawn_interval = spawn_interval
        
        # 管道列表
        self.pipes = []
        
        # 上一次生成管道的时间
        self.last_spawn_time = pygame.time.get_ticks()
        
        # 分数计数器
        self.score = 0
    
    def update(self, current_time):
        """更新所有管道"""
        # 生成新管道
        if current_time - self.last_spawn_time > self.spawn_interval:
            self.spawn_pipe()
            self.last_spawn_time = current_time
        
        # 更新现有管道
        for pipe in self.pipes[:]:
            pipe.update()
            
            # 移除离开屏幕的管道
            if pipe.is_off_screen():
                self.pipes.remove(pipe)
    
    def spawn_pipe(self):
        """生成新管道"""
        # 添加一些随机变化，使游戏更具挑战性
        gap_variation = random.randint(-20, 20)
        gap_size = max(100, min(200, self.pipe_gap + gap_variation))
        
        pipe = Pipe(self.screen_width, self.screen_height, gap_size, 
                   self.pipe_width, self.pipe_speed)
        self.pipes.append(pipe)
    
    def draw(self, screen):
        """绘制所有管道"""
        for pipe in self.pipes:
            pipe.draw(screen)
    
    def check_collisions(self, bird_rect):
        """检查所有管道与鸟的碰撞"""
        for pipe in self.pipes:
            if pipe.collides_with(bird_rect):
                return True
        return False
    
    def check_passed_pipes(self, bird_rect):
        """检查鸟是否通过管道并计分"""
        for pipe in self.pipes:
            if pipe.is_passed(bird_rect.x):
                self.score += 1
                break
        return self.score
    
    def reset(self):
        """重置管道管理器"""
        self.pipes = []
        self.score = 0
        self.last_spawn_time = pygame.time.get_ticks()