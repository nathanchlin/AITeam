// 游戏主循环
function gameLoop() {
  // 1. 处理输入
  // 在键盘事件监听器中调用 snake.changeDirection()
  
  // 2. 移动蛇
  snake.move();
  
  // 3. 检查碰撞
  if (snake.checkWallCollision() || snake.checkSelfCollision()) {
    gameOver();
    return;
  }
  
  // 4. 检查是否吃到食物
  if (snake.head.x === food.x && snake.head.y === food.y) {
    snake.eat();
    generateNewFood();
    score++;
  } else {
    // 如果没有吃到食物，移除尾部
    snake.body.pop();
  }
  
  // 5. 渲染游戏
  render();
  
  // 6. 设置下一次循环
  setTimeout(gameLoop, GAME_SPEED);
}