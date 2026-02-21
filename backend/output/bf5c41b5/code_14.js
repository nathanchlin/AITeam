class Paddle {
  constructor(canvas, paddleWidth = 100, paddleHeight = 15) {
    this.canvas = canvas;
    this.width = paddleWidth;
    this.height = paddleHeight;
    this.x = (canvas.width - paddleWidth) / 2; // 初始位置在中间
    this.y = canvas.height - 30; // 距离底部一定距离
    this.speed = 8; // 挡板移动速度
    this.isMovingLeft = false;
    this.isMovingRight = false;
    
    // 添加键盘事件监听
    this.setupKeyboardControls();
  }
  
  setupKeyboardControls() {
    // 键盘按下事件
    document.addEventListener('keydown', (e) => {
      switch(e.key) {
        case 'ArrowLeft':
          this.isMovingLeft = true;
          e.preventDefault(); // 防止页面滚动
          break;
        case 'ArrowRight':
          this.isMovingRight = true;
          e.preventDefault(); // 防止页面滚动
          break;
      }
    });
    
    // 键盘释放事件
    document.addEventListener('keyup', (e) => {
      switch(e.key) {
        case 'ArrowLeft':
          this.isMovingLeft = false;
          break;
        case 'ArrowRight':
          this.isMovingRight = false;
          break;
      }
    });
  }
  
  update() {
    // 根据按键状态更新挡板位置
    if (this.isMovingLeft) {
      this.x -= this.speed;
    }
    if (this.isMovingRight) {
      this.x += this.speed;
    }
    
    // 添加边界限制，防止挡板移出画布
    if (this.x < 0) {
      this.x = 0;
    }
    if (this.x + this.width > this.canvas.width) {
      this.x = this.canvas.width - this.width;
    }
  }
  
  draw(ctx) {
    // 绘制挡板
    ctx.fillStyle = '#0095DD';
    ctx.fillRect(this.x, this.y, this.width, this.height);
    
    // 添加挡板边框
    ctx.strokeStyle = '#005F8A';
    ctx.lineWidth = 2;
    ctx.strokeRect(this.x, this.y, this.width, this.height);
  }
  
  // 获取挡板矩形区域，用于碰撞检测
  getRect() {
    return {
      x: this.x,
      y: this.y,
      width: this.width,
      height: this.height
    };
  }
}