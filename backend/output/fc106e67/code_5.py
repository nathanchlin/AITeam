def init_background(screen_width, screen_height):
    background = Background(screen_width, screen_height)
    
    # 创建不同层次的背景图像
    # 远景层 (山脉/天空)
    far_layer = pygame.Surface((screen_width, screen_height))
    # 绘制渐变天空
    for y in range(screen_height):
        color_value = int(100 + (155 * y / screen_height))
        pygame.draw.line(far_layer, (color_value, color_value, 255), (0, y), (screen_width, y))
    
    # 添加山脉剪影
    mountain_points = []
    for x in range(0, screen_width + 50, 50):
        height = random.randint(100, 300)
        mountain_points.append((x, screen_height - height))
    mountain_points.append((screen_width, screen_height))
    mountain_points.append((0, screen_height))
    pygame.draw.polygon(far_layer, (50, 50, 100), mountain_points)
    
    background.add_layer(far_layer, 0)  # 最慢滚动
    
    # 中景层 (树木/建筑)
    mid_layer = pygame.Surface((screen_width, screen_height))
    # 添加树木剪影
    for i in range(10):
        x = random.randint(0, screen_width)
        tree_height = random.randint(150, 250)
        pygame.draw.rect(mid_layer, (30, 60, 30), (x, screen_height - tree_height, 20, tree_height))
        pygame.draw.polygon(mid_layer, (20, 40, 20), 
                           [(x-10, screen_height - tree_height), 
                            (x+30, screen_height - tree_height), 
                            (x+10, screen_height - tree_height - 50)])
    
    background.add_layer(mid_layer, 1)
    
    # 近景层 (地面/草)
    near_layer = pygame.Surface((screen_width, screen_height))
    # 绘制地面
    pygame.draw.rect(near_layer, (20, 80, 20), (0, screen_height - 50, screen_width, 50))
    # 添加草的细节
    for x in range(0, screen_width, 10):
        grass_height = random.randint(5, 15)
        pygame.draw.line(near_layer, (10, 60, 10), 
                        (x, screen_height - 50), 
                        (x + random.randint(-3, 3), screen_height - 50 - grass_height), 2)
    
    background.add_layer(near_layer, 2)  # 最快滚动
    
    return background