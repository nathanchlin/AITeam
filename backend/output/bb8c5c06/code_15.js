// 在Renderer类中添加
drawFood(food) {
  // 绘制食物主体
  this.ctx.fillStyle = '#F44336';
  this.ctx.beginPath();
  this.ctx.arc(
    food.x * this.cellSize + this.cellSize / 2,
    food.y * this.cellSize + this.cellSize / 2,
    this.cellSize / 2 - 2,
    0,
    Math.PI * 2
  );
  this.ctx.fill();
  
  // 绘制食物高光
  this.ctx.fillStyle = '#FF8A80';
  this.ctx.beginPath();
  this.ctx.arc(
    food.x * this.cellSize + this.cellSize / 2 - this.cellSize / 4,
    food.y * this.cellSize + this.cellSize / 2 - this.cellSize / 4,
    this.cellSize / 6,
    0,
    Math.PI * 2
  );
  this.ctx.fill();
}