class EditorUI:
    def __init__(self, editor, x, y, width, height):
        self.editor = editor
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.buttons = []
        self.create_buttons()
    
    def create_buttons(self):
        """创建UI按钮"""
        button_y = self.y + 10
        button_height = 30
        button_spacing = 5
        
        # 障碍物类型按钮
        for obstacle_type in ObstacleType:
            button = {
                "rect": pygame.Rect(self.x + 10, button_y, self.width - 20, button_height),
                "text": obstacle_type.value.capitalize(),
                "action": lambda t=obstacle_type: setattr(self.editor, 'selected_obstacle_type', t)
            }
            self.buttons.append(button)
            button_y += button_height + button_spacing
        
        # 工具按钮
        tool_y = button_y + 20
        tools = [
            ("Toggle Grid", lambda: setattr(self.editor, 'show_grid', not self.editor.show_grid)),
            ("Save Level", self.save_level),
            ("Load Level", self.load_level),
            ("Clear Level", self.clear_level)
        ]
        
        for tool_name, tool_action in tools:
            button = {
                "rect": pygame.Rect(self.x + 10, tool_y, self.width - 20, button_height),
                "text": tool_name,
                "action": tool_action
            }
            self.buttons.append(button)
            tool_y += button_height + button_spacing
    
    def draw(self, screen, font):
        """绘制UI"""
        # 绘制背景面板
        pygame.draw.rect(screen, (50, 50, 50), (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, (200, 200, 200), (self.x, self.y, self.width, self.height), 2)
        
        # 绘制按钮
        for button in self.buttons:
            # 高亮当前选中的障碍物类型
            if button["text"] == self.editor.selected_obstacle_type.value.capitalize():
                pygame.draw.rect(screen, (100, 100, 200), button["rect"])
            else:
                pygame.draw.rect(screen, (100, 100, 100), button["rect"])
            
            pygame.draw.rect(screen, (200, 200, 200), button["rect"], 1)
            
            # 绘制文本
            text = font.render(button["text"], True, (255, 255, 255))
            text_rect = text.get_rect(center=button["rect"].center)
            screen.blit(text, text_rect)
    
    def handle_event(self, event):
        """处理UI事件"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            for button in self.buttons:
                if button["rect"].collidepoint(mouse_pos):
                    button["action"]()
                    return True
        return False
    
    def save_level(self):
        """保存当前关卡"""
        filename = f"level_{len(self.editor.obstacles)}.json"
        self.editor.save_level(filename)
        print(f"Level saved to {filename}")
    
    def load_level(self):
        """加载关卡"""
        # 这里可以实现文件选择对话框，简化版使用固定文件名
        try:
            self.editor.load_level("level_1.json")
            print("Level loaded successfully")
        except Exception as e:
            print(f"Failed to load level: {e}")
    
    def clear_level(self):
        """清空当前关卡"""
        self.editor.obstacles.clear()
        self.editor.selected_obstacle = None
        print("Level cleared")