void generate_level_1(GameMap* map) {
    // 清空地图
    for (int y = 0; y < map->height; y++) {
        for (int x = 0; x < map->width; x++) {
            map->grid[y][x].type = BLOCK_EMPTY;
            map->grid[y][x].is_passable = 1;
        }
    }
    
    // 生成地面
    for (int x = 0; x < map->width; x++) {
        map->grid[map->height - 1][x].type = BLOCK_GROUND;
        map->grid[map->height - 1][x].is_passable = 0;
    }
    
    // 第一个平台
    for (int x = 5; x < 15; x++) {
        map->grid[map->height - 5][x].type = BLOCK_BRICK;
        map->grid[map->height - 5][x].is_passable = 0;
    }
    map->grid[map->height - 5][10].type = BLOCK_QUESTION;
    map->grid[map->height - 5][10].has_item = 1;
    
    // 第二个平台
    for (int x = 20; x < 30; x++) {
        map->grid[map->height - 7][x].type = BLOCK_BRICK;
        map->grid[map->height - 7][x].is_passable = 0;
    }
    
    // 第三个平台（带金币）
    for (int x = 35; x < 45; x++) {
        if (x > 35 && x < 44) {
            map->grid[map->height - 9][x].type = BLOCK_COIN;
            map->grid[map->height - 9][x].has_item = 1;
        } else {
            map->grid[map->height - 9][x].type = BLOCK_BRICK;
            map->grid[map->height - 9][x].is_passable = 0;
        }
    }
    
    // 管道障碍
    for (int y = map->height - 6; y < map->height; y++) {
        map->grid[y][50].type = BLOCK_PIPE;
        map->grid[y][50].is_passable = 0;
    }
    
    // 终点
    map->grid[map->height - 2][map->width - 5].type = BLOCK_FLAGPOLE;
    map->grid[map->height - 1][map->width - 5].type = BLOCK_CASTLE;
}