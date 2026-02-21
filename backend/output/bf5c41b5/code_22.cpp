bool checkPaddleCollision(Ball& ball, const Paddle& paddle) {
    // 找到挡板上最接近球的点
    float closestX = std::max(paddle.position.x, 
                             std::min(ball.position.x, paddle.position.x + paddle.width));
    float closestY = std::max(paddle.position.y, 
                             std::min(ball.position.y, paddle.position.y + paddle.height));
    
    // 计算球心到最近点的距离
    float distanceX = ball.position.x - closestX;
    float distanceY = ball.position.y - closestY;
    float distanceSquared = distanceX * distanceX + distanceY * distanceY;
    
    // 如果距离小于球的半径，则发生碰撞
    if (distanceSquared < ball.radius * ball.radius) {
        // 计算碰撞法线
        float distance = sqrt(distanceSquared);
        Vector2 normal = {distanceX / distance, distanceY / distance};
        
        // 将球移出挡板
        ball.position.x = closestX + normal.x * ball.radius;
        ball.position.y = closestY + normal.y * ball.radius;
        
        // 计算反射向量
        float dotProduct = ball.velocity.x * normal.x + ball.velocity.y * normal.y;
        ball.velocity.x = ball.velocity.x - 2 * dotProduct * normal.x;
        ball.velocity.y = ball.velocity.y - 2 * dotProduct * normal.y;
        
        // 根据碰撞位置调整反弹角度
        float hitPosition = (ball.position.x - paddle.position.x) / paddle.width;
        ball.velocity.x = (hitPosition - 0.5f) * 10.0f; // 调整这个值可以改变反弹角度的敏感度
        
        return true;
    }
    
    return false;
}