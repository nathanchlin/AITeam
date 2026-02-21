function gameLoop() {
    // 移动蛇
    snake.move();
    
    // 检查碰撞
    if (snake.checkWallCollision() || snake.checkSelfCollision()) {
        endGame();
        return;
    }
    
    // 其他游戏逻辑...
}