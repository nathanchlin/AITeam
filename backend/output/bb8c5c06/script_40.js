function gameLoop() {
    if (!gameRunning || gamePaused) return;
    
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
        generateFood();
        
        // 每得5分增加游戏速度
        if (score % 5 === 0) {
            gameSpeed = Math.max(50, gameSpeed - SPEED_INCREMENT);
        }
    }
    
    render();
    
    // 继续游戏循环
    setTimeout(gameLoop, gameSpeed);
}