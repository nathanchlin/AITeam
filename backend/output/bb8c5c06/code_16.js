// 在Renderer类中添加
drawGameOver(score) {
  // 半透明覆盖层
  this.ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
  this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
  
  // 游戏结束文字
  this.ctx.font = 'bold 40px Arial';
  this.ctx.fillStyle = 'white';
  this.ctx.textAlign = 'center';
  this.ctx.fillText('游戏结束', this.canvas.width / 2, this.canvas.height / 2 - 30);
  
  // 分数
  this.ctx.font = '24px Arial';
  this.ctx.fillText(`得分: ${score}`, this.canvas.width / 2, this.canvas.height / 2 + 20);
  
  // 重新开始提示
  this.ctx.font = '16px Arial';
  this.ctx.fillText('按空格键重新开始', this.canvas.width / 2, this.canvas.height / 2 + 60);
}