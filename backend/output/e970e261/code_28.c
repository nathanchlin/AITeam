// 主碰撞检测函数
void updateCollisions(Entity* mario, Entity* entities, int entityCount) {
    CollisionBox marioBox = {mario->x, mario->y, mario->width, mario->height};
    
    for (int i = 0; i < entityCount; i++) {
        Entity* other = &entities[i];
        
        if (!other->isAlive || !other->isSolid) continue;
        
        CollisionBox otherBox = {other->x, other->y, other->width, other->height};
        
        if (checkCollisionAABB(marioBox, otherBox)) {
            CollisionInfo info = getCollisionDirection(mario, other);
            handleCollision(mario, other, info);
        }
    }
}