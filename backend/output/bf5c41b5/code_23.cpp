bool checkBrickCollision(Ball& ball, Brick& brick) {
    if (!brick.active) return false;
    
    // 找到砖块上最接近球的点
    float closestX = std::max(brick.position.x, 
                             std::min(ball.position.x, brick.position.x + brick.width));
    float closestY = std::max(brick.position.y, 
                             std::min(ball.position.y, brick.position.y + brick.height));
    
    // 计算球心到最近点的距离
    float distanceX = ball.position.x - closestX;
    float distanceY = ball.position.y - closestY;
    float distanceSquared = distanceX * distanceX + distanceY * distanceY;
    
    // 如果距离小于球的半径，则发生碰撞
    if (distanceSquared < ball.radius * ball.radius) {
        // 计算碰撞法线
        float distance = sqrt(distanceSquared);
        Vector2 normal = {distanceX / distance, distanceY / distance};
        
        // 将球移出砖块
        ball.position.x = closestX + normal.x * ball.radius;
        ball.position.y = closestY + normal.y * ball.radius;
        
        // 计算反射向量
        float dotProduct = ball.velocity.x * normal.x + ball.velocity.y * normal.y;
        ball.velocity.x = ball.velocity.x - 2 * dotProduct * normal.x;
        ball.velocity.y = ball.velocity.y - 2 * dotProduct * normal.y;
        
        // 标记砖块为不活跃
        brick.active = false;
        
        return true;
    }
    
    return false;
}