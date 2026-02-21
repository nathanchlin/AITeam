void render_map(GameMap* map, SDL_Renderer* renderer) {
    // 计算可见区域
    int visible_width = SCREEN_WIDTH / TILE_SIZE + 2;
    int visible_height = SCREEN_HEIGHT / TILE_SIZE + 2;
    
    int start_x = map->camera_x / TILE_SIZE;
    int start_y = map->camera_y / TILE_SIZE;
    
    // 渲染可见区域内的地图块
    for (int y = start_y; y < start_y + visible_height && y < map->height; y++) {
        for (int x = start_x; x < start_x + visible_width && x < map->width; x++) {
            Block* block = &map->grid[y][x];
            
            // 只渲染在屏幕范围内的块
            int screen_x = x * TILE_SIZE - map->camera_x % TILE_SIZE;
            int screen_y = y * TILE_SIZE - map->camera_y % TILE_SIZE;
            
            if (screen_x >= -TILE_SIZE && screen_x < SCREEN_WIDTH && 
                screen_y >= -TILE_SIZE && screen_y < SCREEN_HEIGHT) {
                
                // 根据类型渲染不同的块
                switch (block->type) {
                    case BLOCK_GROUND:
                        render_ground_block(renderer, screen_x, screen_y);
                        break;
                    case BLOCK_BRICK:
                        render_brick_block(renderer, screen_x, screen_y, block->has_item);
                        break;
                    case BLOCK_QUESTION:
                        render_question_block(renderer, screen_x, screen_y, block->has_item);
                        break;
                    case BLOCK_COIN:
                        render_coin_block(renderer, screen_x, screen_y);
                        break;
                    case BLOCK_PIPE:
                        render_pipe(renderer, screen_x, screen_y);
                        break;
                    case BLOCK_FLAGPOLE:
                        render_flagpole(renderer, screen_x, screen_y);
                        break;
                    case BLOCK_CASTLE:
                        render_castle(renderer, screen_x, screen_y);
                        break;
                    default:
                        break;
                }
            }
        }
    }
}