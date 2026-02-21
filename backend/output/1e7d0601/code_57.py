class GameInputHandler:
    def __init__(self, player, game_state):
        self.player = player
        self.game_state = game_state
        
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            # 玩家移动
            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                self.player.move_left = True
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                self.player.move_right = True
            elif event.key == pygame.K_UP or event.key == pygame.K_w:
                self.player.move_up = True
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.player.move_down = True
                
            # 射击
            elif event.key == pygame.K_SPACE:
                self.player.shoot()
                
            # 特殊武器
            elif event.key == pygame.K_LSHIFT:
                self.player.use_special_weapon()
                
            # 暂停游戏
            elif event.key == pygame.K_p:
                self.game_state.toggle_pause()
                
            # 切换武器
            elif event.key == pygame.K_TAB:
                self.player.switch_weapon()
                
        elif event.type == pygame.KEYUP:
            # 停止移动
            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                self.player.move_left = False
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                self.player.move_right = False
            elif event.key == pygame.K_UP or event.key == pygame.K_w:
                self.player.move_up = False
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.player.move_down = False
                
    def handle_continuous_input(self):
        # 处理持续按键输入
        keys = pygame.key.get_pressed()
        
        # 根据按键状态更新玩家移动
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player.move_left = True
        else:
            self.player.move_left = False
            
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player.move_right = True
        else:
            self.player.move_right = False
            
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.player.move_up = True
        else:
            self.player.move_up = False
            
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.player.move_down = True
        else:
            self.player.move_down = False