class Controller:
    def __init__(self):
        self.key_bindings = {
            pygame.K_UP: Direction.UP,
            pygame.K_DOWN: Direction.DOWN,
            pygame.K_LEFT: Direction.LEFT,
            pygame.K_RIGHT: Direction.RIGHT,
            pygame.K_SPACE: self.toggle_pause,
            pygame.K_r: self.restart_game
        }