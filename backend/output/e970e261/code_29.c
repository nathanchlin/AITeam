// 马里奥特定碰撞规则
void applyMarioCollisionRules(Entity* mario, Entity* other) {
    // 无敌状态下的特殊处理
    if (mario->isInvincible) {
        if (other->type == ENTITY_ENEMY) {
            // 无敌状态下可以消灭敌人
            other->isAlive = 0;
            return;
        }
    }
    
    // 大马里奥可以破坏某些方块
    if (mario->isBig && other->type == ENTITY_BLOCK) {
        // 检查是否是可破坏的方块
        if (other->isBreakable) {
            other->isAlive = 0;
            mario->score += 50;
        }
    }
    
    // 滑行状态下的特殊碰撞
    if (mario->isSliding && other->type == ENTITY_ENEMY) {
        // 滑行可以消灭敌人
        other->isAlive = 0;
        mario->score += 200;
    }
}