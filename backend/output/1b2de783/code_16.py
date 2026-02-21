class InputHandler:
    def __init__(self):
        self.keys_pressed = set()
        
    def handle_keydown(self, key):
        if key == pygame.K_LEFT:
            self.keys_pressed.add('left')
        elif key == pygame.K_RIGHT:
            self.keys_pressed.add('right')
        elif key == pygame.K_UP:
            self.keys_pressed.add('up')
        elif key == pygame.K_SPACE:
            self.keys_pressed.add('fire')
            
    def handle_keyup(self, key):
        if key == pygame.K_LEFT:
            self.keys_pressed.discard('left')
        elif key == pygame.K_RIGHT:
            self.keys_pressed.discard('right')
        elif key == pygame.K_UP:
            self.keys_pressed.discard('up')
        elif key == pygame.K_SPACE:
            self.keys_pressed.discard('fire')
            
    def handle_touch(self, touch_type, position, game_width, game_height):
        # 将屏幕划分为控制区域
        left_zone = pygame.Rect(0, game_height * 0.7, game_width * 0.3, game_height * 0.3)
        right_zone = pygame.Rect(game_width * 0.7, game_height * 0.7, game_width * 0.3, game_height * 0.3)
        up_zone = pygame.Rect(game_width * 0.3, game_height * 0.7, game_width * 0.4, game_height * 0.3)
        fire_zone = pygame.Rect(game_width * 0.3, game_height * 0.85, game_width * 0.4, game_height * 0.15)
        
        if touch_type == 'begin':
            if left_zone.collidepoint(position):
                return {'left': True}
            elif right_zone.collidepoint(position):
                return {'right': True}
            elif up_zone.collidepoint(position):
                return {'up': True}
            elif fire_zone.collidepoint(position):
                return {'fire': True}
        elif touch_type == 'end':
            return {'left': False, 'right': False, 'up': False, 'fire': False}
            
        return {}