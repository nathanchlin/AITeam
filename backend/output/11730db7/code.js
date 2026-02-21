// 游戏主模块
class Match3Game {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    this.ctx = this.canvas.getContext('2d');
    
    // 初始化各个子系统
    this.gameState = new GameState();
    this.renderer = new Renderer(this.ctx, this.canvas);
    this.inputHandler = new InputHandler(this.canvas);
    this.levelManager = new LevelManager();
    this.gameLogic = new GameLogic(this.gameState);
    
    // 启动游戏循环
    this.startGameLoop();
  }
  
  startGameLoop() {
    const gameLoop = () => {
      this.update();
      this.render();
      requestAnimationFrame(gameLoop);
    };
    gameLoop();
  }
  
  update() {
    // 更新游戏状态
    this.gameLogic.update();
    this.levelManager.update();
  }
  
  render() {
    // 渲染游戏画面
    this.renderer.render(this.gameState);
  }
}