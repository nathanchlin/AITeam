class PlatformEffects:
    def __init__(self):
        self.breaking_platforms = []
        self.moving_platform_trails = []
    
    def create_break_effect(self, x, y, width, height):
        """创建平台破碎效果"""
        pieces = []
        rows, cols = 4, 4
        piece_width = width / cols
        piece_height = height / rows
        
        for row in range(rows):
            for col in range(cols):
                piece = {
                    'x': x + col * piece_width,
                    'y': y + row * piece_height,
                    'width': piece_width,
                    'height': piece_height,
                    'vx': random.uniform(-5, 5),
                    'vy': random.uniform(-8, -3),
                    'rotation': random.uniform(-10, 10),
                    'rotation_speed': random.uniform(-5, 5),
                    'lifetime': 30,
                    'color': (100, 100, 100)
                }
                pieces.append(piece)
        
        self.breaking_platforms.append(pieces)
    
    def update_breaking_platforms(self):
        """更新所有破碎的平台效果"""
        for pieces in self.breaking_platforms[:]:
            for piece in pieces[:]:
                piece['x'] += piece['vx']
                piece['y'] += piece['vy']
                piece['vy'] += 0.5  # 重力
                piece['rotation'] += piece['rotation_speed']
                piece['lifetime'] -= 1
                
                if piece['lifetime'] <= 0:
                    pieces.remove(piece)
            
            if not pieces:
                self.breaking_platforms.remove(pieces)
    
    def draw_breaking_platforms(self, screen):
        """绘制所有破碎的平台效果"""
        for pieces in self.breaking_platforms:
            for piece in pieces:
                # 创建一个旋转的矩形表面
                surf = pygame.Surface((piece['width'], piece['height']), pygame.SRCALPHA)
                surf.fill(piece['color'])
                
                # 旋转表面
                rotated = pygame.transform.rotate(surf, piece['rotation'])
                rect = rotated.get_rect(center=(piece['x'] + piece['width']/2, 
                                              piece['y'] + piece['height']/2))
                
                screen.blit(rotated, rect)