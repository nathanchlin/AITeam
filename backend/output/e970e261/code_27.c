// 碰撞信息结构
typedef struct {
    int direction; // COLLISION_FROM_TOP, COLLISION_FROM_BOTTOM, etc.
    int overlapX;
    int overlapY;
} CollisionInfo;

// 获取碰撞方向
CollisionInfo getCollisionDirection(Entity* a, Entity* b) {
    CollisionInfo info;
    info.direction = COLLISION_NONE;
    
    // 计算重叠量
    int overlapX = min(a->x + a->width, b->x + b->width) - max(a->x, b->x);
    int overlapY = min(a->y + a->height, b->y + b->height) - max(a->y, b->y);
    
    // 判断主要碰撞方向
    if (overlapX > overlapY) {
        if (a->y < b->y) {
            info.direction = COLLISION_FROM_TOP;
        } else {
            info.direction = COLLISION_FROM_BOTTOM;
        }
        info.overlapY = overlapY;
    } else {
        if (a->x < b->x) {
            info.direction = COLLISION_FROM_LEFT;
        } else {
            info.direction = COLLISION_FROM_RIGHT;
        }
        info.overlapX = overlapX;
    }
    
    return info;
}