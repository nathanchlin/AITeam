class FlappyBirdGame {
  constructor() {
    this.canvas = document.getElementById('gameCanvas');
    this.ctx = this.canvas.getContext('2d');
    this.scoreSystem = new ScoreSystem();
    this.pipes = [];
    this.bird = {
      x: 50,
      y: 150,
      velocity: 0,
      radius: 15
    };
    this.gameStarted = false;
    this.gameOver = false;
    
    this.init();
  }

  init() {
    // 初始化计分系统
    this.scoreSystem.init(this.canvas.parentElement);
    
    // 事件监听
    this.canvas.addEventListener('click', () => this.handleJump());
    document.addEventListener('keydown', (e) => {
      if (e.code === 'Space') {
        this.handleJump();
      }
    });
    
    // 开始游戏循环
    this.gameLoop();
  }

  handleJump() {
    if (!this.gameStarted) {
      this.gameStarted = true;
    } else if (this.gameOver) {
      this.resetGame();
    } else {
      this.bird.velocity = -5;
    }
  }

  resetGame() {
    this.bird.y = 150;
    this.bird.velocity = 0;
    this.pipes = [];
    this.scoreSystem.resetScore();
    this.gameOver = false;
    this.gameStarted = false;
  }

  update() {
    if (!this.gameStarted || this.gameOver) return;
    
    // 更新鸟的位置
    this.bird.velocity += 0.5; // 重力
    this.bird.y += this.bird.velocity;
    
    // 生成新管道
    if (this.pipes.length === 0 || this.pipes[this.pipes.length - 1].x < this.canvas.width - 200) {
      const gapY = Math.random() * (this.canvas.height - 200) + 100;
      this.pipes.push({
        x: this.canvas.width,
        topHeight: gapY - 100,
        bottomY: gapY + 100,
        passed: false
      });
    }
    
    // 更新管道位置
    for (let i = this.pipes.length - 1; i >= 0; i--) {
      this.pipes[i].x -= 2;
      
      // 检查是否通过管道
      if (!this.pipes[i].passed && this.pipes[i].x + 50 < this.bird.x) {
        this.pipes[i].passed = true;
        this.scoreSystem.increaseScore();
      }
      
      // 移除屏幕外的管道
      if (this.pipes[i].x + 50 < 0) {
        this.pipes.splice(i, 1);
      }
    }
    
    // 碰撞检测
    if (this.checkCollision()) {
      this.gameOver = true;
    }
  }

  checkCollision() {
    // 检查是否撞到上下边界
    if (this.bird.y - this.bird.radius < 0 || this.bird.y + this.bird.radius > this.canvas.height) {
      return true;
    }
    
    // 检查是否撞到管道
    for (const pipe of this.pipes) {
      if (this.bird.x + this.bird.radius > pipe.x && this.bird.x - this.bird.radius < pipe.x + 50) {
        if (this.bird.y - this.bird.radius < pipe.topHeight || this.bird.y + this.bird.radius > pipe.bottomY) {
          return true;
        }
      }
    }
    
    return false;
  }

  draw() {
    // 清空画布
    this.ctx.fillStyle = 'skyblue';
    this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
    
    // 绘制鸟
    this.ctx.fillStyle = 'yellow';
    this.ctx.beginPath();
    this.ctx.arc(this.bird.x, this.bird.y, this.bird.radius, 0, Math.PI * 2);
    this.ctx.fill();
    
    // 绘制管道
    this.ctx.fillStyle = 'green';
    for (const pipe of this.pipes) {
      // 上管道
      this.ctx.fillRect(pipe.x, 0, 50, pipe.topHeight);
      // 下管道
      this.ctx.fillRect(pipe.x, pipe.bottomY, 50, this.canvas.height - pipe.bottomY);
    }
    
    // 游戏结束提示
    if (this.gameOver) {
      this.ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
      this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
      this.ctx.fillStyle = 'white';
      this.ctx.font = '30px Arial';
      this.ctx.textAlign = 'center';
      this.ctx.fillText('Game Over!', this.canvas.width / 2, this.canvas.height / 2 - 30);
      this.ctx.fillText('Click to Restart', this.canvas.width / 2, this.canvas.height / 2 + 30);
    }
    
    // 游戏开始提示
    if (!this.gameStarted && !this.gameOver) {
      this.ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
      this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
      this.ctx.fillStyle = 'white';
      this.ctx.font = '30px Arial';
      this.ctx.textAlign = 'center';
      this.ctx.fillText('Click to Start', this.canvas.width / 2, this.canvas.height / 2);
    }
  }

  gameLoop() {
    this.update();
    this.draw();
    requestAnimationFrame(() => this.gameLoop());
  }
}

// 启动游戏
window.addEventListener('DOMContentLoaded', () => {
  const game = new FlappyBirdGame();
});