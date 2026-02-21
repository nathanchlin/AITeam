// 初始化画布
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

// 创建挡板实例
const paddle = new Paddle(canvas);

// 游戏循环
function gameLoop() {
  // 清空画布
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  
  // 更新挡板位置
  paddle.update();
  
  // 绘制挡板
  paddle.draw(ctx);
  
  // 继续游戏循环
  requestAnimationFrame(gameLoop);
}

// 启动游戏
gameLoop();