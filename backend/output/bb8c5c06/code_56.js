if (foodGenerator.checkCollision(snake.body[0])) {
    snake.growSnake();
    score += 10;
    updateScore();
    
    // 增加速度
    currentSpeed = Math.max(50, currentSpeed - SPEED_INCREMENT);
    
    // 重新生成食物
    foodGenerator.generate(snake.body);
    
    // 重新设置游戏循环
    clearInterval(gameInterval);
    gameInterval = setInterval(gameLoop, currentSpeed);
}