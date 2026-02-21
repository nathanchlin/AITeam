// 马里奥状态枚举
typedef enum {
    MARIO_STATE_IDLE,
    MARIO_STATE_WALKING,
    MARIO_STATE_RUNNING,
    MARIO_STATE_JUMPING,
    MARIO_STATE_FALLING,
    MARIO_STATE_DUCKING
} MarioState;

// 马里奥方向枚举
typedef enum {
    MARIO_DIR_RIGHT,
    MARIO_DIR_LEFT
} MarioDirection;

// 马里奥结构体
typedef struct {
    // 位置和速度
    float x;
    float y;
    float velocity_x;
    float velocity_y;
    
    // 状态和方向
    MarioState state;
    MarioDirection direction;
    
    // 控制参数
    bool is_jumping;
    bool is_ducking;
    int jump_count;
    int max_jumps;
    
    // 动画相关
    int animation_frame;
    int animation_timer;
    
    // 物理参数
    float walk_speed;
    float run_speed;
    float jump_strength;
    float gravity;
    float friction;
} Mario;

// 初始化马里奥
void init_mario(Mario* mario, float x, float y) {
    mario->x = x;
    mario->y = y;
    mario->velocity_x = 0;
    mario->velocity_y = 0;
    mario->state = MARIO_STATE_IDLE;
    mario->direction = MARIO_DIR_RIGHT;
    mario->is_jumping = false;
    mario->is_ducking = false;
    mario->jump_count = 0;
    mario->max_jumps = 2; // 允许二段跳
    mario->animation_frame = 0;
    mario->animation_timer = 0;
    
    // 物理参数
    mario->walk_speed = 2.0f;
    mario->run_speed = 4.0f;
    mario->jump_strength = -12.0f;
    mario->gravity = 0.5f;
    mario->friction = 0.85f;
}

// 处理输入
void handle_input(Mario* mario, bool left_pressed, bool right_pressed, bool up_pressed, bool down_pressed, bool action_pressed) {
    // 水平移动
    if (left_pressed) {
        mario->velocity_x -= 0.5f;
        mario->direction = MARIO_DIR_LEFT;
        
        if (mario->state == MARIO_STATE_IDLE) {
            mario->state = MARIO_STATE_WALKING;
        }
    }
    
    if (right_pressed) {
        mario->velocity_x += 0.5f;
        mario->direction = MARIO_DIR_RIGHT;
        
        if (mario->state == MARIO_STATE_IDLE) {
            mario->state = MARIO_STATE_WALKING;
        }
    }
    
    // 跳跃
    if (up_pressed && mario->jump_count < mario->max_jumps) {
        mario->velocity_y = mario->jump_strength;
        mario->is_jumping = true;
        mario->jump_count++;
        mario->state = MARIO_STATE_JUMPING;
    }
    
    // 下蹲
    if (down_pressed) {
        mario->is_ducking = true;
        mario->state = MARIO_STATE_DUCKING;
    } else {
        mario->is_ducking = false;
        if (mario->state == MARIO_STATE_DUCKING && mario->velocity_y == 0) {
            mario->state = MARIO_STATE_IDLE;
        }
    }
    
    // 动作键（如奔跑）
    if (action_pressed && (left_pressed || right_pressed)) {
        mario->state = MARIO_STATE_RUNNING;
    }
    
    // 限制速度
    if (mario->velocity_x > mario->run_speed) {
        mario->velocity_x = mario->run_speed;
    } else if (mario->velocity_x < -mario->run_speed) {
        mario->velocity_x = -mario->run_speed;
    } else if (mario->velocity_x > mario->walk_speed && mario->velocity_x < mario->walk_speed) {
        mario->velocity_x = (mario->velocity_x > 0) ? mario->walk_speed : -mario->walk_speed;
    }
}

// 更新马里奥状态
void update_mario(Mario* mario) {
    // 应用重力
    if (mario->is_jumping || mario->velocity_y != 0) {
        mario->velocity_y += mario->gravity;
        
        if (mario->velocity_y > 0) {
            mario->state = MARIO_STATE_FALLING;
        }
    }
    
    // 应用摩擦力
    if (!left_pressed && !right_pressed) {
        mario->velocity_x *= mario->friction;
        
        if (fabs(mario->velocity_x) < 0.1f) {
            mario->velocity_x = 0;
            if (mario->state != MARIO_STATE_JUMPING && mario->state != MARIO_STATE_FALLING) {
                mario->state = MARIO_STATE_IDLE;
            }
        }
    }
    
    // 更新位置
    mario->x += mario->velocity_x;
    mario->y += mario->velocity_y;
    
    // 更新动画
    mario->animation_timer++;
    if (mario->animation_timer > 10) {
        mario->animation_timer = 0;
        mario->animation_frame = (mario->animation_frame + 1) % 4;
    }
    
    // 检查是否落地
    if (mario->y >= GROUND_LEVEL) {
        mario->y = GROUND_LEVEL;
        mario->velocity_y = 0;
        mario->is_jumping = false;
        mario->jump_count = 0;
        
        if (mario->state == MARIO_STATE_FALLING) {
            mario->state = MARIO_STATE_IDLE;
        }
    }
}

// 渲染马里奥
void render_mario(Mario* mario) {
    // 根据状态和方向选择精灵
    int sprite_id = 0;
    
    if (mario->is_ducking) {
        sprite_id = 4; // 下蹲精灵
    } else {
        switch (mario->state) {
            case MARIO_STATE_IDLE:
                sprite_id = 0;
                break;
            case MARIO_STATE_WALKING:
                sprite_id = (mario->animation_frame / 2) % 2 + 1;
                break;
            case MARIO_STATE_RUNNING:
                sprite_id = (mario->animation_frame / 2) % 2 + 3;
                break;
            case MARIO_STATE_JUMPING:
            case MARIO_STATE_FALLING:
                sprite_id = 5;
                break;
            default:
                sprite_id = 0;
        }
    }
    
    // 根据方向翻转精灵
    if (mario->direction == MARIO_DIR_LEFT) {
        // 水平翻转渲染
        draw_sprite_flipped(mario->x, mario->y, sprite_id);
    } else {
        draw_sprite(mario->x, mario->y, sprite_id);
    }
}