import pygame
import sys

class InputHandler:
    def __init__(self, state_manager: GameStateManager):
        self.state_manager = state_manager
        self.use_pygame = False
        
        # 检查是否可以使用pygame
        try:
            pygame.init()
            self.use_pygame = True
            self.clock = pygame.time.Clock()
        except:
            self.use_pygame = False
    
    def handle_input(self):
        if self.use_pygame:
            self._handle_pygame_input()
        else:
            self._handle_console_input()
    
    def _handle_pygame_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.state_manager.stop()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.state_manager.change_direction(Direction.UP)
                elif event.key == pygame.K_DOWN:
                    self.state_manager.change_direction(Direction.DOWN)
                elif event.key == pygame.K_LEFT:
                    self.state_manager.change_direction(Direction.LEFT)
                elif event.key == pygame.K_RIGHT:
                    self.state_manager.change_direction(Direction.RIGHT)
                elif event.key == pygame.K_SPACE:
                    self.state_manager.toggle_pause()
                elif event.key == pygame.K_ESCAPE:
                    self.state_manager.stop()
    
    def _handle_console_input(self):
        import select
        import sys
        
        # 检查是否有输入
        if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
            key = sys.stdin.read(1).lower()
            
            if key == 'w':
                self.state_manager.change_direction(Direction.UP)
            elif key == 's':
                self.state_manager.change_direction(Direction.DOWN)
            elif key == 'a':
                self.state_manager.change_direction(Direction.LEFT)
            elif key == 'd':
                self.state_manager.change_direction(Direction.RIGHT)
            elif key == ' ':
                self.state_manager.toggle_pause()
            elif key == 'q':
                self.state_manager.stop()