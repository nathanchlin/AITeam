class GameStateManager:
    def __init__(self, config: GameConfig):
        self.config = config
        self.state = self._initialize_game()
        self.observers = []
        
    def _initialize_game(self) -> GameState:
        # 初始蛇的位置在屏幕中央
        start_x = self.config.grid_width // 2
        start_y = self.config.grid_height // 2
        snake_body = [
            Position(start_x - i, start_y) 
            for i in range(self.config.initial_snake_length)
        ]
        snake = Snake(snake_body, Direction.RIGHT)
        
        # 生成第一个食物
        food = self._generate_food(snake)
        
        return GameState(snake=snake, food=[food], score=0)
    
    def _generate_food(self, snake: Snake) -> Food:
        import random
        while True:
            x = random.randint(0, self.config.grid_width - 1)
            y = random.randint(0, self.config.grid_height - 1)
            pos = Position(x, y)
            
            # 确保食物不会生成在蛇身上
            if pos not in snake.body:
                return Food(pos)
    
    def update(self, dt: float):
        if self.state.is_game_over or self.state.is_paused:
            return
            
        # 更新蛇的位置
        self.state.snake.move()
        
        # 检查碰撞
        if self._check_collision():
            self.state.is_game_over = True
            return
            
        # 检查是否吃到食物
        self._check_food_collision()
        
        # 通知观察者状态变化
        self.notify_observers()
    
    def _check_collision(self) -> bool:
        head = self.state.snake.body[0]
        
        # 检查是否撞墙
        if (head.x < 0 or head.x >= self.config.grid_width or 
            head.y < 0 or head.y >= self.config.grid_height):
            return True
            
        # 检查是否撞到自己
        if head in self.state.snake.body[1:]:
            return True
            
        return False
    
    def _check_food_collision(self):
        head = self.state.snake.body[0]
        for food in self.state.food[:]:
            if head == food.position:
                # 吃到食物
                self.state.snake.move(grow=True)
                self.state.score += self.config.score_per_food
                self.state.food.remove(food)
                self.state.food.append(self._generate_food(self.state.snake))
    
    def change_direction(self, direction: Direction):
        # 防止蛇直接掉头
        opposite = {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT
        }
        
        if direction != opposite.get(self.state.snake.direction):
            self.state.snake.next_direction = direction
    
    def toggle_pause(self):
        self.state.is_paused = not self.state.is_paused
    
    def add_observer(self, observer):
        self.observers.append(observer)
    
    def notify_observers(self):
        for observer in self.observers:
            observer.on_state_changed(self.state)