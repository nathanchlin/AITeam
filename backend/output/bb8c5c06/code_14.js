// 在Renderer类中添加
drawSnake(snake) {
  snake.body.forEach((segment, index) => {
    if (index === 0) {
      // 蛇头
      this.ctx.fillStyle = '#4CAF50';
      this.ctx.fillRect(
        segment.x * this.cellSize,
        segment.y * this.cellSize,
        this.cellSize,
        this.cellSize
      );
      
      // 绘制眼睛
      this.ctx.fillStyle = 'white';
      const eyeSize = this.cellSize / 5;
      const eyeOffset = this.cellSize / 3;
      
      // 根据蛇的方向确定眼睛位置
      if (snake.direction === 'right') {
        this.ctx.fillRect(
          segment.x * this.cellSize + this.cellSize - eyeOffset - eyeSize,
          segment.y * this.cellSize + eyeOffset,
          eyeSize,
          eyeSize
        );
        this.ctx.fillRect(
          segment.x * this.cellSize + this.cellSize - eyeOffset - eyeSize,
          segment.y * this.cellSize + this.cellSize - eyeOffset - eyeSize,
          eyeSize,
          eyeSize
        );
      } else if (snake.direction === 'left') {
        this.ctx.fillRect(
          segment.x * this.cellSize + eyeOffset,
          segment.y * this.cellSize + eyeOffset,
          eyeSize,
          eyeSize
        );
        this.ctx.fillRect(
          segment.x * this.cellSize + eyeOffset,
          segment.y * this.cellSize + this.cellSize - eyeOffset - eyeSize,
          eyeSize,
          eyeSize
        );
      } else if (snake.direction === 'up') {
        this.ctx.fillRect(
          segment.x * this.cellSize + eyeOffset,
          segment.y * this.cellSize + eyeOffset,
          eyeSize,
          eyeSize
        );
        this.ctx.fillRect(
          segment.x * this.cellSize + this.cellSize - eyeOffset - eyeSize,
          segment.y * this.cellSize + eyeOffset,
          eyeSize,
          eyeSize
        );
      } else if (snake.direction === 'down') {
        this.ctx.fillRect(
          segment.x * this.cellSize + eyeOffset,
          segment.y * this.cellSize + this.cellSize - eyeOffset - eyeSize,
          eyeSize,
          eyeSize
        );
        this.ctx.fillRect(
          segment.x * this.cellSize + this.cellSize - eyeOffset - eyeSize,
          segment.y * this.cellSize + this.cellSize - eyeOffset - eyeSize,
          eyeSize,
          eyeSize
        );
      }
    } else {
      // 蛇身
      this.ctx.fillStyle = '#388E3C';
      this.ctx.fillRect(
        segment.x * this.cellSize,
        segment.y * this.cellSize,
        this.cellSize,
        this.cellSize
      );
    }
    
    // 绘制边框
    this.ctx.strokeStyle = '#1B5E20';
    this.ctx.lineWidth = 1;
    this.ctx.strokeRect(
      segment.x * this.cellSize,
      segment.y * this.cellSize,
      this.cellSize,
      this.cellSize
    );
  });
}