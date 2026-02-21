// 渲染地面块
void render_ground_block(SDL_Renderer* renderer, int x, int y) {
    SDL_Rect rect = {x, y, TILE_SIZE, TILE_SIZE};
    SDL_SetRenderDrawColor(renderer, 139, 69, 19, 255); // 棕色
    SDL_RenderFillRect(renderer, &rect);
    
    // 添加纹理细节
    SDL_SetRenderDrawColor(renderer, 101, 67, 33, 255);
    for (int i = 0; i < TILE_SIZE; i += 4) {
        SDL_RenderDrawLine(renderer, x, y + i, x + TILE_SIZE, y + i);
    }
}

// 渲染砖块
void render_brick_block(SDL_Renderer* renderer, int x, int y, int has_item) {
    SDL_Rect rect = {x, y, TILE_SIZE, TILE_SIZE};
    SDL_SetRenderDrawColor(renderer, 178, 34, 34, 255); // 红色
    SDL_RenderFillRect(renderer, &rect);
    
    // 砖块纹理
    SDL_SetRenderDrawColor(renderer, 139, 0, 0, 255);
    SDL_RenderDrawLine(renderer, x, y + TILE_SIZE/2, x + TILE_SIZE, y + TILE_SIZE/2);
    SDL_RenderDrawLine(renderer, x + TILE_SIZE/2, y, x + TILE_SIZE/2, y + TILE_SIZE);
    
    // 如果有物品，添加问号
    if (has_item) {
        SDL_SetRenderDrawColor(renderer, 255, 255, 255, 255);
        render_text(renderer, "?", x + TILE_SIZE/2 - 4, y + TILE_SIZE/2 - 8);
    }
}

// 渲染管道
void render_pipe(SDL_Renderer* renderer, int x, int y) {
    // 管道主体
    SDL_SetRenderDrawColor(renderer, 0, 128, 0, 255); // 绿色
    SDL_Rect rect = {x, y, TILE_SIZE, TILE_SIZE * 2};
    SDL_RenderFillRect(renderer, &rect);
    
    // 管道顶部
    SDL_SetRenderDrawColor(renderer, 0, 100, 0, 255);
    SDL_Rect top = {x - 4, y - 4, TILE_SIZE + 8, 8};
    SDL_RenderFillRect(renderer, &top);
}