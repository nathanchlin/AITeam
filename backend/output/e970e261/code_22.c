int main() {
    // 初始化SDL
    SDL_Init(SDL_INIT_VIDEO);
    SDL_Window* window = SDL_CreateWindow("Mario-like Game", 
                                          SDL_WINDOWPOS_UNDEFINED, 
                                          SDL_WINDOWPOS_UNDEFINED, 
                                          SCREEN_WIDTH, SCREEN_HEIGHT, 0);
    SDL_Renderer* renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED);
    
    // 创建关卡管理器
    LevelManager* level_manager = create_level_manager();
    
    // 创建玩家
    Player* player = create_player();
    
    // 游戏主循环
    int running = 1;
    while (running) {
        // 处理事件
        SDL_Event event;
        while (SDL_PollEvent(&event)) {
            if (event.type == SDL_QUIT) {
                running = 0;
            }
            // 处理玩家输入
            handle_player_input(player, event);
        }
        
        // 更新玩家
        update_player(player, level_manager->map);
        
        // 更新相机
        update_camera(level_manager->map, player);
        
        // 渲染
        SDL_SetRenderDrawColor(renderer, 135, 206, 235, 255); // 天蓝色背景
        SDL_RenderClear(renderer);
        
        // 渲染地图
        render_map(level_manager->map, renderer);
        
        // 渲染玩家
        render_player(renderer, player);
        
        SDL_RenderPresent(renderer);
        
        // 控制帧率
        SDL_Delay(16); // 约60FPS
    }
    
    // 清理资源
    destroy_level_manager(level_manager);
    destroy_player(player);
    SDL_DestroyRenderer(renderer);
    SDL_DestroyWindow(window);
    SDL_Quit();
    
    return 0;
}