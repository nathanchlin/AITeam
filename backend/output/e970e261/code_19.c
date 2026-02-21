typedef struct {
    GameMap* map;
    int current_level;
    LevelGeneratorConfig generator_config;
} LevelManager;

LevelManager* create_level_manager() {
    LevelManager* manager = (LevelManager*)malloc(sizeof(LevelManager));
    manager->current_level = 1;
    manager->map = create_map(200, 20); // 200x20的地图
    
    // 设置生成器配置
    manager->generator_config.min_platform_length = 3;
    manager->generator_config.max_platform_length = 8;
    manager->generator_config.min_platform_gap = 2;
    manager->generator_config.max_platform_gap = 5;
    manager->generator_config.obstacle_probability = 0.7;
    manager->generator_config.coin_probability = 0.3;
    manager->generator_config.powerup_probability = 0.1;
    
    // 加载第一关
    load_level(manager, 1);
    
    return manager;
}

void load_level(LevelManager* manager, int level) {
    // 根据关卡编号加载关卡
    if (level == 1) {
        generate_level_1(manager->map);
    } else {
        // 随着关卡增加提高难度
        manager->generator_config.min_platform_length = 3 + level / 2;
        manager->generator_config.max_platform_length = 8 + level / 2;
        manager->generator_config.obstacle_probability = min(0.9, 0.7 + level * 0.05);
        generate_random_level(manager->map, manager->generator_config);
    }
    
    manager->current_level = level;
}