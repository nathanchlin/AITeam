class GameUI:
    def __init__(self, screen):
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        
        # 游戏区域和HUD区域划分
        self.game_area = pygame.Rect(0, 0, self.width, self.height - 100)
        self.hud_area = pygame.Rect(0, self.height - 100, self.width, 100)
        
        # 小地图
        self.minimap_size = 120
        self.minimap_rect = pygame.Rect(self.width - self.minimap_size - 10, 10, self.minimap_size, self.minimap_size)
        
        # 武器指示器
        self.weapon_indicator = pygame.Rect(10, self.height - 90, 200, 30)
        
        # 能量条
        self.energy_bar = pygame.Rect(10, self.height - 50, 200, 20)
        self.energy_fill = 100
        
    def draw(self, game_state):
        # 绘制游戏区域背景
        pygame.draw.rect(self.screen, (0, 0, 30), self.game_area)
        
        # 绘制HUD区域背景
        pygame.draw.rect(self.screen, (20, 20, 50), self.hud_area)
        pygame.draw.line(self.screen, (100, 100, 100), 
                        (0, self.height - 100), 
                        (self.width, self.height - 100), 2)
        
        # 绘制小地图
        self.draw_minimap(game_state.enemies, game_state.player)
        
        # 绘制武器指示器
        self.draw_weapon_indicator(game_state.player)
        
        # 绘制能量条
        self.draw_energy_bar(game_state.player)
        
    def draw_minimap(self, enemies, player):
        # 绘制小地图背景
        pygame.draw.rect(self.screen, (10, 10, 30), self.minimap_rect)
        pygame.draw.rect(self.screen, (100, 100, 100), self.minimap_rect, 1)
        
        # 计算缩放比例
        scale_x = self.minimap_size / self.width
        scale_y = self.minimap_size / self.height
        
        # 绘制玩家在小地图上的位置
        player_x = int(player.rect.centerx * scale_x)
        player_y = int(player.rect.centery * scale_y)
        pygame.draw.circle(self.screen, (0, 255, 0), 
                          (self.minimap_rect.x + player_x, self.minimap_rect.y + player_y), 3)
        
        # 绘制敌人在小地图上的位置
        for enemy in enemies:
            enemy_x = int(enemy.rect.centerx * scale_x)
            enemy_y = int(enemy.rect.centery * scale_y)
            pygame.draw.circle(self.screen, (255, 0, 0), 
                              (self.minimap_rect.x + enemy_x, self.minimap_rect.y + enemy_y), 2)
            
    def draw_weapon_indicator(self, player):
        # 绘制武器指示器背景
        pygame.draw.rect(self.screen, (30, 30, 60), self.weapon_indicator)
        pygame.draw.rect(self.screen, (100, 100, 100), self.weapon_indicator, 1)
        
        # 绘制当前武器类型
        weapon_text = f"Weapon: {player.current_weapon}"
        text_surface = pygame.font.Font("assets/fonts/retro.ttf", 18).render(weapon_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.weapon_indicator.center)
        self.screen.blit(text_surface, text_rect)
        
        # 绘制弹药数量
        ammo_text = f"Ammo: {player.ammo}/{player.max_ammo}"
        ammo_surface = pygame.font.Font("assets/fonts/retro.ttf", 16).render(ammo_text, True, (255, 255, 0))
        self.screen.blit(ammo_surface, (self.weapon_indicator.right + 10, self.weapon_indicator.centery - 10))
        
    def draw_energy_bar(self, player):
        # 绘制能量条背景
        pygame.draw.rect(self.screen, (30, 30, 60), self.energy_bar)
        pygame.draw.rect(self.screen, (100, 100, 100), self.energy_bar, 1)
        
        # 计算能量条填充
        fill_width = int(self.energy_bar.width * (player.energy / 100))
        fill_rect = pygame.Rect(self.energy_bar.x, self.energy_bar.y, fill_width, self.energy_bar.height)
        
        # 根据能量值改变颜色
        if player.energy > 60:
            color = (0, 255, 0)
        elif player.energy > 30:
            color = (255, 255, 0)
        else:
            color = (255, 0, 0)
            
        pygame.draw.rect(self.screen, color, fill_rect)
        
        # 绘制能量文本
        energy_text = f"Energy: {int(player.energy)}%"
        text_surface = pygame.font.Font("assets/fonts/retro.ttf", 16).render(energy_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.energy_bar.center)
        self.screen.blit(text_surface, text_rect)