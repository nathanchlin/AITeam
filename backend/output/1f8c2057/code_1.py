@dataclass
class GameConfig:
    grid_width: int
    grid_height: int
    initial_snake_length: int = 3
    game_speed: int = 10  # moves per second
    score_per_food: int = 10
    super_food_score: int = 50

@dataclass
class GameState:
    snake: Snake
    food: List[Food]
    score: int
    is_game_over: bool = False
    is_paused: bool = False
    level: int = 1