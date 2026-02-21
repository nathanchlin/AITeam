int main() {
    // 初始化游戏
    Entity mario = {50, 300, 16, 32, ENTITY_MARIO, 1, 1};
    mario.velocityX = 0;
    mario.velocityY = 0;
    
    // 创建地图实体
    Entity entities[] = {
        {100, 300, 32, 32, ENTITY_BLOCK, 1, 1},     // 地面方块
        {200, 200, 32, 32, ENTITY_BLOCK, 1, 1},     // 悬浮方块
        {250, 280, 16, 16, ENTITY_COIN, 0, 1},       // 金币
        {300, 300, 32, 32, ENTITY_ENEMY, 1, 1},      // 敌人
        {400, 300, 64, 64, ENTITY_PIPE, 1, 1}       // 管道
    };
    
    int entityCount = sizeof(entities) / sizeof(entities[0]);
    
    // 游戏主循环
    while (gameRunning) {
        // 更新马里奥位置
        updateMarioPosition(&mario);
        
        // 执行碰撞检测
        updateCollisions(&mario, entities, entityCount);
        
        // 渲染游戏
        renderGame(&mario, entities, entityCount);
    }
    
    return 0;
}