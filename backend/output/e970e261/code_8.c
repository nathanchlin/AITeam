// 物理系统初始化
void physics_init(PhysicsSystem* physics) {
    physics->gravity = 0.5;
    physics->friction = 0.9;
    physics->air_resistance = 0.99;
}

// 更新物体物理状态
void update_physics(PhysicsSystem* physics, GameObject* obj) {
    // 应用重力
    if (obj->flags & OBJ_FLAG_GRAVITY) {
        obj->velocity_y += physics->gravity;
    }
    
    // 应用摩擦力
    if (obj->on_ground) {
        obj->velocity_x *= physics->friction;
    } else {
        obj->velocity_x *= physics->air_resistance;
    }
    
    // 更新位置
    obj->x += obj->velocity_x;
    obj->y += obj->velocity_y;
    
    // 简单的碰撞检测
    check_collisions(obj);
}

// 碰撞检测
void check_collisions(GameObject* obj) {
    // 这里简化了碰撞检测，实际实现需要遍历所有对象
    // 或使用空间分区数据结构优化
    
    // 地面碰撞
    if (obj->y + obj->height > GROUND_LEVEL) {
        obj->y = GROUND_LEVEL - obj->height;
        obj->velocity_y = 0;
        obj->on_ground = 1;
        obj->flags &= ~OBJ_FLAG_JUMPING;
    } else {
        obj->on_ground = 0;
    }
    
    // 墙壁碰撞
    if (obj->x < 0) {
        obj->x = 0;
        obj->velocity_x = 0;
    } else if (obj->x + obj->width > SCREEN_WIDTH) {
        obj->x = SCREEN_WIDTH - obj->width;
        obj->velocity_x = 0;
    }
}