// 在Renderer类中添加
render(gameState) {
  // 清空画布
  this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
  
  // 绘制网格背景
  this.drawGrid();
  
  // 根据游戏状态绘制不同内容
  if (gameState === 'start') {
    this.drawStartScreen();
  } else if (gameState === 'playing') {
    this.drawSnake(game.snake);
    this.drawFood(game.food);
  } else if (gameState === 'gameOver') {
    this.drawSnake(game.snake);
    this.drawFood(game.food);
    this.drawGameOver(game.score);
  }
}