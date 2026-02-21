# 初始化资源管理器
resource_manager = ResourceManager()

# 添加游戏资源
def load_game_resources():
    # 飞机精灵
    resource_manager.add_image('player_plane', 'assets/sprites/player_plane.png')
    resource_manager.add_image('enemy_plane1', 'assets/sprites/enemy_plane1.png')
    resource_manager.add_image('enemy_plane2', 'assets/sprites/enemy_plane2.png')
    
    # 子弹精灵
    resource_manager.add_image('player_bullet', 'assets/sprites/player_bullet.png')
    resource_manager.add_image('enemy_bullet', 'assets/sprites/enemy_bullet.png')
    
    # 爆炸效果
    resource_manager.add_image('explosion1', 'assets/sprites/explosion1.png')
    resource_manager.add_image('explosion2', 'assets/sprites/explosion2.png')
    
    # 背景元素
    resource_manager.add_image('cloud1', 'assets/background/cloud1.png')
    resource_manager.add_image('cloud2', 'assets/background/cloud2.png')
    
    # 音效
    resource_manager.add_sound('shoot', 'assets/sounds/shoot.wav')
    resource_manager.add_sound('explosion', 'assets/sounds/explosion.wav')
    resource_manager.add_sound('bg_music', 'assets/sounds/background_music.mp3')
    
    # UI元素
    resource_manager.add_image('game_over', 'assets/ui/game_over.png')
    resource_manager.add_image('start_button', 'assets/ui/start_button.png')

# 游戏主循环中的资源加载
def game_loading_screen(screen):
    font = pygame.font.SysFont('Arial', 36)
    loading_text = font.render("Loading...", True, (255, 255, 255))
    
    while resource_manager.load_next():
        # 更新加载进度
        progress = resource_manager.get_progress()
        
        # 绘制加载屏幕
        screen.fill((0, 0, 0))
        screen.blit(loading_text, (screen.get_width()//2 - loading_text.get_width()//2, 
                                  screen.get_height()//2 - loading_text.get_height()//2))
        
        # 绘制进度条
        bar_width = 400
        bar_height = 20
        bar_x = screen.get_width()//2 - bar_width//2
        bar_y = screen.get_height()//2 + 50
        
        pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)
        pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, int(bar_width * progress), bar_height))
        
        pygame.display.flip()
        pygame.time.wait(10)