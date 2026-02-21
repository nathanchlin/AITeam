typedef struct {
    int min_platform_length;
    int max_platform_length;
    int min_platform_gap;
    int max_platform_gap;
    float obstacle_probability;
    float coin_probability;
    float powerup_probability;
} LevelGeneratorConfig;

// 生成随机关卡
void generate_random_level(GameMap* map, LevelGeneratorConfig config) {
    // 生成地面
    for (int x = 0; x < map->width; x++) {
        map->grid[map->height - 1][x].type = BLOCK_GROUND;
        map->grid[map->height - 1][x].is_passable = 0;
    }
    
    // 生成平台和障碍物
    int current_x = 5;
    int platform_y = map->height - 5;
    
    while (current_x < map->width - 10) {
        // 随机平台长度
        int platform_length = random_int(config.min_platform_length, config.max_platform_length);
        
        // 生成平台
        for (int x = current_x; x < current_x + platform_length && x < map->width; x++) {
            if (x > current_x) { // 平台两端不生成砖块
                map->grid[platform_y][x].type = BLOCK_BRICK;
                map->grid[platform_y][x].is_passable = 0;
                
                // 随机生成物品
                float rand = (float)rand() / RAND_MAX;
                if (rand < config.coin_probability) {
                    map->grid[platform_y][x].type = BLOCK_COIN;
                    map->grid[platform_y][x].has_item = 1;
                } else if (rand < config.coin_probability + config.powerup_probability) {
                    map->grid[platform_y][x].type = BLOCK_QUESTION;
                    map->grid[platform_y][x].has_item = 1;
                }
            }
        }
        
        // 随机间隙
        int gap = random_int(config.min_platform_gap, config.max_platform_gap);
        current_x += platform_length + gap;
        
        // 随机平台高度变化
        platform_y = random_int(max(5, platform_y - 2), min(map->height - 3, platform_y + 2));
    }
    
    // 添加终点元素
    map->grid[map->height - 2][map->width - 5].type = BLOCK_FLAGPOLE;
    map->grid[map->height - 1][map->width - 5].type = BLOCK_CASTLE;
}