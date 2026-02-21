// 在Renderer类中添加
drawGrid() {
  this.ctx.fillStyle = '#111';
  this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
  
  this.ctx.strokeStyle = '#333';
  this.ctx.lineWidth = 0.5;
  
  // 绘制垂直线
  for (let i = 0; i <= this.gridSize; i++) {
    this.ctx.beginPath();
    this.ctx.moveTo(i * this.cellSize, 0);
    this.ctx.lineTo(i * this.cellSize, this.canvas.height);
    this.ctx.stroke();
  }
  
  // 绘制水平线
  for (let i = 0; i <= this.gridSize; i++) {
    this.ctx.beginPath();
    this.ctx.moveTo(0, i * this.cellSize);
    this.ctx.lineTo(this.canvas.width, i * this.cellSize);
    this.ctx.stroke();
  }
}