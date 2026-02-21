// 在Renderer类中添加
drawStartScreen() {
  // 半透明覆盖层
  this.ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
  this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
  
  // 游戏标题
  this.ctx.font = 'bold 40px Arial';
  this.ctx.fillStyle = '#4CAF50';
  this.ctx.textAlign = 'center';
  this.ctx.fillText('贪吃蛇', this.canvas.width / 2, this.canvas.height / 2 - 30);
  
  // 开始提示
  this.ctx.font = '20px Arial';
  this.ctx.fillStyle = 'white';
  this.ctx.fillText('按空格键开始游戏', this.canvas.width / 2, this.canvas.height / 2 + 20);
  
  // 控制说明
  this.ctx.font = '16px Arial';
  this.ctx.fillText('使用方向键控制蛇的移动', this.canvas.width / 2, this.canvas.height / 2 + 60);
}