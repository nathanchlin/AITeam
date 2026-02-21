class Renderer {
  constructor(canvas, gridSize) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.gridSize = gridSize;
    this.cellSize = Math.min(
      canvas.width / gridSize,
      canvas.height / gridSize
    );
    
    // 设置画布尺寸
    this.canvas.width = this.cellSize * gridSize;
    this.canvas.height = this.cellSize * gridSize;
  }
  
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
  
  render(game) {
    // 清空画布
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    
    // 绘制网格背景
    this.drawGrid();
    
    // 根据游戏状态绘制不同内容
    if (game.state === 'start') {
      this.drawStartScreen();
    } else if (game.state === 'playing') {
      this.drawSnake(game.snake);
      this.drawFood(game.food);
    } else if (game.state === 'gameOver') {
      this.drawSnake(game.snake);
      this.drawFood(game.food);
      this.drawGameOver(game.score);
    }
  }
}