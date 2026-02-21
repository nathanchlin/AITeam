// 马里奥对象初始化
void mario_init(GameObject* mario) {
    mario->x = 100;
    mario->y = GROUND_LEVEL - MARIO_HEIGHT;
    mario->width = MARIO_WIDTH;
    mario->height = MARIO_HEIGHT;
    mario->velocity_x = 0;
    mario->velocity_y = 0;
    mario->on_ground = 1;
    
    // 设置马里奥属性
    mario->flags = OBJ_FLAG_GRAVITY | OBJ_FLAG_PLAYER;
    mario->sprite = &mario_sprites[0]; // 默认站立精灵
    
    // 设置碰撞箱
    mario->collision_box = (Rect){0, 0, MARIO_WIDTH, MARIO_HEIGHT};
}

// 更新马里奥状态
void update_mario(GameObject* mario, InputState* input) {
    // 左右移动
    if (input->left) {
        mario->velocity_x = -MARIO_SPEED;
        mario->direction = -1;
    } else if (input->right) {
        mario->velocity_x = MARIO_SPEED;
        mario->direction = 1;
    } else {
        mario->velocity_x *= 0.8; // 摩擦力
    }
    
    // 跳跃
    if (input->jump && mario->on_ground) {
        mario->velocity_y = -MARIO_JUMP_POWER;
        mario->flags |= OBJ_FLAG_JUMPING;
    }
    
    // 更新精灵状态
    if (mario->velocity_x != 0) {
        if (abs(mario->velocity_x) > 2) {
            // 快速移动 - 跑步精灵
            mario->sprite = &mario_sprites[1 + ((int)(SDL_GetTicks() / 100) % 2)];
        } else {
            // 慢速移动 - 行走精灵
            mario->sprite = &mario_sprites[2 + ((int)(SDL_GetTicks() / 200) % 2)];
        }
    } else {
        // 静止 - 站立精灵
        mario->sprite = &mario_sprites[0];
    }
}