class UIElement:
    def __init__(self, x, y, width, height, color, border_color=None, border_width=2):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.border_color = border_color
        self.border_width = border_width
        self.hover = False
        self.click = False
    
    def draw(self, screen):
        """绘制UI元素"""
        # 绘制主体
        pygame.draw.rect(screen, self.color, self.rect, border_radius=5)
        
        # 绘制边框
        if self.border_color:
            pygame.draw.rect(screen, self.border_color, self.rect, 
                            self.border_width, border_radius=5)
        
        # 悬停效果
        if self.hover:
            hover_surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            hover_surf.fill((255, 255, 255, 30))
            screen.blit(hover_surf, self.rect)
        
        # 点击效果
        if self.click:
            click_surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            click_surf.fill((0, 0, 0, 50))
            screen.blit(click_surf, self.rect)

class Button(UIElement):
    def __init__(self, x, y, width, height, text, font, color=(70, 130, 180), 
                 hover_color=(100, 160, 210), text_color=(255, 255, 255)):
        super().__init__(x, y, width, height, color)
        self.text = text
        self.font = font
        self.hover_color = hover_color
        self.text_color = text_color
        self.original_color = color
    
    def draw(self, screen):
        """绘制按钮"""
        # 更新颜色
        if self.hover:
            self.color = self.hover_color
        else:
            self.color = self.original_color
        
        # 绘制按钮背景
        super().draw(screen)
        
        # 绘制文本
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

class ScoreDisplay:
    def __init__(self, x, y, font):
        self.x = x
        self.y = y
        self.font = font
        self.score = 0
        self.high_score = 0
        self.combo = 0
        self.max_combo = 0
        self.score_animations = []
    
    def add_score(self, points, combo=1):
        """添加分数并创建动画"""
        self.score += points * combo
        self.combo = combo
        
        if combo > self.max_combo:
            self.max_combo = combo
        
        # 创建分数动画
        animation = {
            'text': f"+{points * combo}",
            'x': self.x + 100,
            'y': self.y,
            'vy': -2,
            'lifetime': 60,
            'color': (255, 215, 0) if combo > 1 else (255, 255, 255)
        }
        self.score_animations.append(animation)
    
    def update(self):
        """更新分数显示"""
        for anim in self.score_animations[:]:
            anim['y'] += anim['vy']
            anim['lifetime'] -= 1
            
            if anim['lifetime'] <= 0:
                self.score_animations.remove(anim)
    
    def draw(self, screen):
        """绘制分数显示"""
        # 绘制当前分数
        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        screen.blit(score_text, (self.x, self.y))
        
        # 绘制最高分
        high_score_text = self.font.render(f"High Score: {self.high_score}", True, (255, 215, 0))
        screen.blit(high_score_text, (self.x, self.y + 30))
        
        # 绘制连击
        if self.combo > 1:
            combo_text = self.font.render(f"Combo x{self.combo}!", True, (255, 100, 100))
            screen.blit(combo_text, (self.x, self.y + 60))
        
        # 绘制分数动画
        for anim in self.score_animations:
            alpha = anim['lifetime'] / 60
            text = self.font.render(anim['text'], True, anim['color'])
            text.set_alpha(int(255 * alpha))
            screen.blit(text, (anim['x'], anim['y']))