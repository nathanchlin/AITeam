// 渲染系统初始化
void render_init(RenderSystem* render, int width, int height) {
    render->width = width;
    render->height = height;
    render->pixels = malloc(width * height * sizeof(uint8_t));
    render->palette = create_8bit_palette();
    
    // 初始化8位风格调色板
    render->palette[0] = (Color){0x00, 0x00, 0x00}; // 黑色
    render->palette[1] = (Color){0x9C, 0x73, 0x35}; // 棕色
    render->palette[2] = (Color){0xBC, 0x90, 0x4E}; // 浅棕色
    render->palette[3] = (Color){0x00, 0x78, 0x00}; // 绿色
    // ... 更多8位颜色
}

// 绘制精灵（8位风格）
void draw_sprite(RenderSystem* render, Sprite* sprite, int x, int y) {
    for (int row = 0; row < sprite->height; row++) {
        for (int col = 0; col < sprite->width; col++) {
            uint8_t pixel = sprite->data[row * sprite->width + col];
            if (pixel != 0) { // 0表示透明
                int screen_x = x + col;
                int screen_y = y + row;
                if (screen_x >= 0 && screen_x < render->width && 
                    screen_y >= 0 && screen_y < render->height) {
                    render->pixels[screen_y * render->width + screen_x] = pixel;
                }
            }
        }
    }
}

// 简单的瓦片地图渲染
void render_tilemap(RenderSystem* render, Tilemap* tilemap, int camera_x, int camera_y) {
    int start_x = camera_x / TILE_SIZE;
    int start_y = camera_y / TILE_SIZE;
    int end_x = (camera_x + render->width) / TILE_SIZE + 1;
    int end_y = (camera_y + render->height) / TILE_SIZE + 1;
    
    for (int y = start_y; y < end_y && y < tilemap->height; y++) {
        for (int x = start_x; x < end_x && x < tilemap->width; x++) {
            int tile_index = tilemap->data[y * tilemap->width + x];
            if (tile_index != 0) {
                Sprite* tile = &tilemap->tiles[tile_index - 1];
                draw_sprite(render, tile, 
                           x * TILE_SIZE - camera_x, 
                           y * TILE_SIZE - camera_y);
            }
        }
    }
}