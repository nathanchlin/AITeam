// 游戏主循环
void game_loop(GameEngine* engine) {
    Uint32 last_time = SDL_GetTicks();
    
    while (engine->state != GAME_STATE_EXIT) {
        Uint32 current_time = SDL_GetTicks();
        float delta_time = (current_time - last_time) / 1000.0f;
        last_time = current_time;
        
        // 处理输入
        handle_input(engine);
        
        // 更新物理
        for (int i = 0; i < engine->object_count; i++) {
            update_physics(&engine->physics, engine->objects[i]);
            
            // 如果是马里奥，特殊处理
            if (engine->objects[i]->flags & OBJ_FLAG_PLAYER) {
                update_mario(engine->objects[i], &engine->input);
            }
        }
        
        // 更新相机（跟随马里奥）
        update_camera(engine);
        
        // 渲染
        render_clear(&engine->render);
        
        // 渲染游戏对象
        for (int i = 0; i < engine->object_count; i++) {
            if (engine->objects[i]->sprite) {
                draw_sprite(&engine->render, engine->objects[i]->sprite,
                           engine->objects[i]->x - engine->camera_x,
                           engine->objects[i]->y - engine->camera_y);
            }
        }
        
        // 渲染UI
        render_ui(&engine->render);
        
        // 呈现
        render_present(&engine->render);
        
        // 控制帧率（60FPS）
        SDL_Delay(1000/60 - (SDL_GetTicks() - current_time));
    }
}