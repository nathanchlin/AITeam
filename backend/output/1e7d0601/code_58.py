class UIManager:
    def __init__(self, screen):
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        
        # 初始化UI组件
        self.main_menu = MainMenu(screen)
        self.hud = GameHUD(screen)
        self.game_ui = GameUI(screen)
        
        # 当前UI状态
        self.current_state = "MAIN_MENU"
        
    def update(self, game_state):
        if self.current_state == "MAIN_MENU":
            self.main_menu.update()
        elif self.current_state == "GAME":
            self.hud.update(game_state.player, game_state.enemies, game_state.powerups)
            
    def draw(self, game_state):
        if self.current_state == "MAIN_MENU":
            self.main_menu.draw()
        elif self.current_state == "GAME":
            self.game_ui.draw(game_state)
            self.hud.draw()
            
    def handle_input(self, event, game_state):
        if self.current_state == "MAIN_MENU":
            selected_item = self.main_menu.handle_input(event)
            if selected_item:
                if selected_item == "开始游戏":
                    self.current_state = "GAME"
                    game_state.reset_game()
                elif selected_item == "设置":
                    # 打开设置菜单
                    pass
                elif selected_item == "排行榜":
                    # 显示排行榜
                    pass
                elif selected_item == "退出":
                    return False  # 退出游戏
                    
        elif self.current_state == "GAME":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.current_state = "MAIN_MENU"
                    
        return True  # 继续游戏