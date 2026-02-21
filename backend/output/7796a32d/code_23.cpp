// 简单的AABB碰撞检测
bool checkAABBCollision(const Rect& a, const Rect& b) {
    return a.x < b.x + b.width &&
           a.x + a.width > b.x &&
           a.y < b.y + b.height &&
           a.y + a.height > b.y;
}

// 扩展的AABB碰撞检测，返回碰撞方向
CollisionDirection checkAABBCollisionWithDirection(const Rect& a, const Rect& b) {
    CollisionDirection direction = { false, false, false, false }; // 上, 下, 左, 右
    
    float overlapX = std::min(a.x + a.width - b.x, b.x + b.width - a.x);
    float overlapY = std::min(a.y + a.height - b.y, b.y + b.height - a.y);
    
    if (overlapX < overlapY) {
        // 水平碰撞
        if (a.x < b.x) {
            direction.left = true;
        } else {
            direction.right = true;
        }
    } else {
        // 垂直碰撞
        if (a.y < b.y) {
            direction.top = true;
        } else {
            direction.bottom = true;
        }
    }
    
    return direction;
}