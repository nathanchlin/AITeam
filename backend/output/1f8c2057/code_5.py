import pygame

class PygameRenderer(Renderer):
    def __init__(self, config: GameConfig):
        self.config = config
        pygame.init()
        self.cell_size = 20
        self.screen_width = config.grid_width * self.cell_size
        self.screen_height = config.grid_height * self.cell_size
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Snake Game")
        
        # 颜色定义
        self.colors = {
            'background': (0, 0, 0),
            'snake': (0, 255, 0),
            'snake_head': (0, 200, 0),
            'food': (255, 0, 0),
            'super_food': (255, 255, 0),
            'text': (255, 255, 255)
        }
        
        self.font = pygame.font.SysFont(None, 36)
    
    def render(self, state: GameState):
        self.screen.fill(self.colors['background'])
        
        # 渲染蛇
        for i, segment in enumerate(state.snake.body):
            color = self.colors['snake_head'] if i == 0 else self.colors['snake']
            rect = pygame.Rect(
                segment.x * self.cell_size,
                segment.y * self.cell_size,
                self.cell_size,
                self.cell_size
            )
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, (0, 0, 0), rect, 1)  # 边框
        
        # 渲染食物
        for food in state.food:
            color = self.colors['super_food'] if food.type == "super" else self.colors['food']
            rect = pygame.Rect(
                food.position.x * self.cell_size,
                food.position.y * self.cell_size,
                self.cell_size,
                self.cell_size
            )
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, (0, 0, 0), rect, 1)  # 边框
        
        # 渲染分数
        score_text = self.font.render(f"Score: {state.score}", True, self.colors['text'])
        self.screen.blit(score_text, (10, 10))
        
        if state.is_game_over:
            game_over_text = self.font.render("Game Over!", True, self.colors['text'])
            text_rect = game_over_text.get_rect(center=(self.screen_width/2, self.screen_height/2))
            self.screen.blit(game_over_text, text_rect)
        elif state.is_paused:
            pause_text = self.font.render("Paused", True, self.colors['text'])
            text_rect = pause_text.get_rect(center=(self.screen_width/2, self.screen_height/2))
            self.screen.blit(pause_text, text_rect)
        
        pygame.display.flip()
    
    def clear(self):
        self.screen.fill(self.colors['background'])
        pygame.display.flip()