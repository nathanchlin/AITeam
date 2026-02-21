class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        
        # 菜单选项
        self.menu_items = ["开始游戏", "设置", "排行榜", "退出"]
        self.selected_item = 0
        
        # UI元素
        self.background = pygame.image.load("assets/main_menu_bg.png")
        self.title_font = pygame.font.Font("assets/fonts/retro.ttf", 72)
        self.menu_font = pygame.font.Font("assets/fonts/retro.ttf", 36)
        
        # 动画元素
        self.plane_y = 0
        self.plane_direction = 1
        
    def update(self):
        # 更新飞机动画
        self.plane_y += self.plane_direction * 2
        if self.plane_y > 20 or self.plane_y < -20:
            self.plane_direction *= -1
            
    def draw(self):
        # 绘制背景
        self.screen.blit(self.background, (0, 0))
        
        # 绘制标题
        title_text = self.title_font.render("1942", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.width // 2, 100))
        self.screen.blit(title_text, title_rect)
        
        # 绘制菜单选项
        for i, item in enumerate(self.menu_items):
            color = (255, 255, 0) if i == self.selected_item else (255, 255, 255)
            menu_text = self.menu_font.render(item, True, color)
            menu_rect = menu_text.get_rect(center=(self.width // 2, 250 + i * 60))
            self.screen.blit(menu_text, menu_rect)
            
        # 绘制装饰性飞机
        plane_img = pygame.image.load("assets/player_plane.png")
        plane_rect = plane_img.get_rect(center=(self.width // 2, 400 + self.plane_y))
        self.screen.blit(plane_img, plane_rect)
        
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_item = (self.selected_item - 1) % len(self.menu_items)
            elif event.key == pygame.K_DOWN:
                self.selected_item = (self.selected_item + 1) % len(self.menu_items)
            elif event.key == pygame.K_RETURN:
                return self.menu_items[self.selected_item]
        return None