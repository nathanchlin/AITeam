const collisionLayers = {
    bullet: 0,    // 最高优先级
    tank: 1,
    obstacle: 2   // 最低优先级
};

function handleCollisions() {
    // 先处理子弹碰撞
    checkBulletCollisions();
    // 然后处理坦克碰撞
    checkTankCollisions();
    // 最后处理坦克与障碍物碰撞
    checkTankObstacleCollisions();
}