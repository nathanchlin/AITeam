GameMap* create_map(int width, int height) {
    GameMap* map = (GameMap*)malloc(sizeof(GameMap));
    map->width = width;
    map->height = height;
    map->camera_x = 0;
    map->camera_y = 0;
    
    // 分配二维数组
    map->grid = (Block**)malloc(height * sizeof(Block*));
    for (int y = 0; y < height; y++) {
        map->grid[y] = (Block*)malloc(width * sizeof(Block));
        for (int x = 0; x < width; x++) {
            map->grid[y][x].type = BLOCK_EMPTY;
            map->grid[y][x].x = x;
            map->grid[y][x].y = y;
            map->grid[y][x].is_visible = 0;
            map->grid[y][x].has_item = 0;
            map->grid[y][x].is_passable = 1;
        }
    }
    
    return map;
}