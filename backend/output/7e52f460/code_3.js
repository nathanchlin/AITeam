// 检查是否吃到食物
if (head.x === food.x && head.y === food.y) {
    // 增加分数
    score += 10;
    scoreElement.textContent = score;
    
    // 更新最高分
    if (score > highScore) {
        highScore = score;
        highScoreElement.textContent = highScore;
        localStorage.setItem('snakeHighScore', highScore);
    }
    
    // 生成新食物
    generateFood();
    
    // 增加游戏速度
    currentSpeed = Math.max(50, currentSpeed - SPEED_INCREMENT);
    clearInterval(gameInterval);
    gameInterval = setInterval(gameLoop, currentSpeed);
} else {
    // 如果没有吃到食物，移除蛇尾
    snake.pop();
}