// 检测两个AABB是否碰撞
int checkCollisionAABB(CollisionBox a, CollisionBox b) {
    return (a.x < b.x + b.width &&
            a.x + a.width > b.x &&
            a.y < b.y + b.height &&
            a.y + a.height > b.y);
}