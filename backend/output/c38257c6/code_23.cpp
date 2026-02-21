bool checkPaddleCollision(Ball& ball, const Paddle& paddle) {
    // 找到球心在挡板坐标系中的位置
    float relativeX = ball.position.x - paddle.position.x;
    float normalizedX = relativeX / (paddle.width / 2);
    
    // 检查是否在挡板范围内
    if (std::abs(normalizedX) <= 1.0f && 
        ball.position.y + ball.radius >= paddle.position.y - paddle.height/2 &&
        ball.position.y - ball.radius <= paddle.position.y + paddle.height/2) {
        
        // 计算碰撞点相对于挡板中心的位置
        float hitPosition = normalizedX;
        
        // 根据碰撞位置调整反弹角度
        float maxAngle = 75.0f * (M_PI / 180.0f); // 最大反弹角度
        float angle = hitPosition * maxAngle;
        
        // 计算新速度方向
        float speed = ball.velocity.length();
        ball.velocity.x = speed * sin(angle);
        ball.velocity.y = -speed * cos(angle);
        
        // 确保球不会卡在挡板内
        ball.position.y = paddle.position.y - paddle.height/2 - ball.radius;
        
        return true;
    }
    
    return false;
}