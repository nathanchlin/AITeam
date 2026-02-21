function gameLoop() {
    if (!gameRunning) return;
    
    // 移动蛇
    snake.move();
    
    // 检查碰撞
    if (snake.checkCollision()) {
        gameOver();
        return;
    }
    
    // 检查是否吃到食物
    if (snake.eat(food)) {
        score++;
        scoreElement.textContent = `得分: ${score}`;
        
        // 增加游戏难度
        if (score % 5 === 0 && gameSpeed > 50) {
            gameSpeed -= SPEED_INCREMENT;
            clearInterval(gameLoopInterval);
            gameLoopInterval = setInterval(gameLoop, gameSpeed);
        }
        
        generateFood();
    }
    
    // 渲染游戏
    render();
}