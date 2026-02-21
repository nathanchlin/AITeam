// 游戏类
class PacmanGame {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    this.gameMap = new GameMap(19, 19); // 19x19的地图
    this.renderer = new Renderer(this.canvas, this.gameMap);
    this.running = false;
    
    // 初始化地图
    this.gameMap.createSimpleMaze();
  }

  // 开始游戏
  start() {
    this.running = true;
    this.gameLoop();
  }

  // 游戏主循环
  gameLoop() {
    if (!this.running) return;
    
    this.renderer.render();
    requestAnimationFrame(() => this.gameLoop());
  }

  // 停止游戏
  stop() {
    this.running = false;
  }
}

// 初始化并启动游戏
window.onload = () => {
  const game = new PacmanGame('gameCanvas');
  game.start();
  
  // 添加键盘控制
  document.addEventListener('keydown', (e) => {
    // 这里可以添加吃豆人的移动逻辑
    console.log('Key pressed:', e.key);
  });
};