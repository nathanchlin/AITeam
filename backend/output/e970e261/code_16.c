void update_camera(GameMap* map, Player* player) {
    // 相机跟随玩家，但限制在地图范围内
    map->camera_x = player->x - SCREEN_WIDTH / 2;
    map->camera_y = player->y - SCREEN_HEIGHT / 2;
    
    // 限制相机在地图范围内
    if (map->camera_x < 0) map->camera_x = 0;
    if (map->camera_y < 0) map->camera_y = 0;
    if (map->camera_x > map->width * TILE_SIZE - SCREEN_WIDTH) {
        map->camera_x = map->width * TILE_SIZE - SCREEN_WIDTH;
    }
    if (map->camera_y > map->height * TILE_SIZE - SCREEN_HEIGHT) {
        map->camera_y = map->height * TILE_SIZE - SCREEN_HEIGHT;
    }
}