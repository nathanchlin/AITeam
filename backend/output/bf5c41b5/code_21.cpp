void checkBoundaryCollision(Ball& ball, float screenWidth, float screenHeight) {
    // 左右边界碰撞
    if (ball.position.x - ball.radius <= 0) {
        ball.position.x = ball.radius;
        ball.velocity.x = -ball.velocity.x;
    } else if (ball.position.x + ball.radius >= screenWidth) {
        ball.position.x = screenWidth - ball.radius;
        ball.velocity.x = -ball.velocity.x;
    }
    
    // 上边界碰撞
    if (ball.position.y - ball.radius <= 0) {
        ball.position.y = ball.radius;
        ball.velocity.y = -ball.velocity.y;
    }
    
    // 下边界碰撞（游戏结束条件）
    if (ball.position.y + ball.radius >= screenHeight) {
        // 游戏结束逻辑
        return false; // 表示游戏结束
    }
    
    return true; // 游戏继续
}