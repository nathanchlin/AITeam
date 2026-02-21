bool checkBrickCollision(Ball& ball, Brick& brick) {
    // 找到球心在砖块坐标系中的位置
    float closestX = std::clamp(ball.position.x, brick.left, brick.right);
    float closestY = std::clamp(ball.position.y, brick.top, brick.bottom);
    
    // 计算球心到最近点的距离
    float distanceX = ball.position.x - closestX;
    float distanceY = ball.position.y - closestY;
    float distanceSquared = distanceX * distanceX + distanceY * distanceY;
    
    // 检查是否碰撞
    if (distanceSquared <= ball.radius * ball.radius) {
        // 计算碰撞法线
        float distance = std::sqrt(distanceSquared);
        Vector2 normal(distanceX / distance, distanceY / distance);
        
        // 计算相对速度在法线方向上的分量
        float velocityAlongNormal = dot(ball.velocity, normal);
        
        // 如果球正在远离砖块，不处理碰撞
        if (velocityAlongNormal > 0) {
            return false;
        }
        
        // 计算反弹后的速度
        ball.velocity -= (1 + PhysicsConfig().restitution) * velocityAlongNormal * normal;
        
        // 将球移出砖块
        float overlap = ball.radius - distance;
        ball.position += normal * overlap;
        
        return true;
    }
    
    return false;
}