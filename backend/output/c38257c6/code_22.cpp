bool checkWallCollision(Ball& ball, const GameArea& gameArea) {
    bool collision = false;
    
    // 左右墙壁碰撞
    if (ball.position.x - ball.radius <= gameArea.left) {
        ball.position.x = gameArea.left + ball.radius;
        ball.velocity.x = -ball.velocity.x * PhysicsConfig().restitution;
        collision = true;
    }
    else if (ball.position.x + ball.radius >= gameArea.right) {
        ball.position.x = gameArea.right - ball.radius;
        ball.velocity.x = -ball.velocity.x * PhysicsConfig().restitution;
        collision = true;
    }
    
    // 顶部墙壁碰撞
    if (ball.position.y - ball.radius <= gameArea.top) {
        ball.position.y = gameArea.top + ball.radius;
        ball.velocity.y = -ball.velocity.y * PhysicsConfig().restitution;
        collision = true;
    }
    
    return collision;
}