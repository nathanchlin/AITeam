// 检查玩家与地图块的碰撞
int check_collision(GameMap* map, Player* player) {
    // 计算玩家占据的地图块范围
    int left = player->x / TILE_SIZE;
    int right = (player->x + player->width) / TILE_SIZE;
    int top = player->y / TILE_SIZE;
    int bottom = (player->y + player->height) / TILE_SIZE;
    
    // 检查每个碰撞的块
    for (int y = top; y <= bottom; y++) {
        for (int x = left; x <= right; x++) {
            if (x >= 0 && x < map->width && y >= 0 && y < map->height) {
                Block* block = &map->grid[y][x];
                if (!block->is_passable) {
                    // 简单的AABB碰撞检测
                    SDL_Rect player_rect = {player->x, player->y, player->width, player->height};
                    SDL_Rect block_rect = {x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE};
                    
                    if (SDL_HasIntersection(&player_rect, &block_rect)) {
                        return 1; // 发生碰撞
                    }
                }
            }
        }
    }
    
    return 0; // 无碰撞
}