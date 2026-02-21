// 碰撞响应处理
void handleCollision(Entity* mario, Entity* other, CollisionInfo info) {
    switch (other->type) {
        case ENTITY_BLOCK:
            // 处理与方块的碰撞
            if (info.direction == COLLISION_FROM_TOP) {
                mario->y = other->y - mario->height;
                mario->isJumping = 0;
                mario->velocityY = 0;
            } else if (info.direction == COLLISION_FROM_BOTTOM) {
                mario->y = other->y + other->height;
                mario->velocityY = 0;
            } else if (info.direction == COLLISION_FROM_LEFT) {
                mario->x = other->x - mario->width;
            } else if (info.direction == COLLISION_FROM_RIGHT) {
                mario->x = other->x + other->width;
            }
            break;
            
        case ENTITY_ENEMY:
            // 处理与敌人的碰撞
            if (info.direction == COLLISION_FROM_TOP) {
                // 踩踏敌人
                other->isAlive = 0;
                mario->velocityY = -8; // 小跳跃
            } else {
                // 马里奥受伤
                mario->lives--;
                // 重置位置或无敌时间等
            }
            break;
            
        case ENTITY_COIN:
            // 收集金币
            if (!other->isCollected) {
                other->isCollected = 1;
                mario->score += 100;
            }
            break;
            
        case ENTITY_PIPE:
            // 进入管道
            if (info.direction == COLLISION_FROM_TOP) {
                // 处理进入管道逻辑
            }
            break;
    }
}