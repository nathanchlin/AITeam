class GameLogic:
    def __init__(self, width, height):
        self.grid_width = width
        self.grid_height = height
        self.snake = Snake()
        self.food = Food()
        self.game_state = GameState.RUNNING
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT