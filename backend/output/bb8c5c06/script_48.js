function gameLoop() {
  if (!gameRunning) return;
  
  // 移动蛇
  const ateFood = snake.move();
  
  // 检查碰撞
  if (snake.checkCollision()) {
    gameOver();
    return;
  }
  
  // 检查是否吃到食物
  if (snake.checkFoodCollision(food)) {
    score++;
    scoreElement.textContent = `得分: ${score}`;
    snake.grow();
    generateFood();
    
    // 每得5分增加游戏速度
    if (score % 5 === 0) {
      currentSpeed = Math.max(50, currentSpeed - SPEED_INCREMENT);
    }
  }
  
  render();
  
  // 使用setTimeout控制游戏速度
  setTimeout(gameLoop, currentSpeed);
}