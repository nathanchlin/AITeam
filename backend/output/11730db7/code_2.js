class Renderer {
  constructor(ctx, canvas) {
    this.ctx = ctx;
    this.canvas = canvas;
    this.tileSize = 50; // 每个格子的大小
    this.padding = 5; // 格子间距
    this.assetLoader = new AssetLoader();
  }
  
  render(gameState) {
    // 清空画布
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    
    // 渲染背景
    this.renderBackground();
    
    // 渲染游戏网格
    this.renderGrid(gameState.grid);
    
    // 渲染UI元素
    this.renderUI(gameState);
  }
  
  renderBackground() {
    this.ctx.fillStyle = '#f0f0f0';
    this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
  }
  
  renderGrid(grid) {
    const startX = (this.canvas.width - (grid.width * (this.tileSize + this.padding))) / 2;
    const startY = (this.canvas.height - (grid.height * (this.tileSize + this.padding))) / 2;
    
    for (let row = 0; row < grid.height; row++) {
      for (let col = 0; col < grid.width; col++) {
        const x = startX + col * (this.tileSize + this.padding);
        const y = startY + row * (this.tileSize + this.padding);
        
        if (grid[row][col]) {
          this.renderTile(x, y, grid[row][col]);
        }
      }
    }
  }
  
  renderTile(x, y, type) {
    // 根据类型渲染不同颜色的方块
    const colors = {
      'red': '#FF5252',
      'blue': '#448AFF',
      'green': '#69F0AE',
      'yellow': '#FFD740',
      'purple': '#E040FB'
    };
    
    this.ctx.fillStyle = colors[type] || '#CCCCCC';
    this.ctx.fillRect(x, y, this.tileSize, this.tileSize);
    
    // 添加边框
    this.ctx.strokeStyle = '#333333';
    this.ctx.lineWidth = 1;
    this.ctx.strokeRect(x, y, this.tileSize, this.tileSize);
  }
  
  renderUI(gameState) {
    // 渲染得分
    this.ctx.fillStyle = '#333333';
    this.ctx.font = '20px Arial';
    this.ctx.fillText(`Score: ${gameState.score}`, 20, 30);
    
    // 渲染当前关卡
    this.ctx.fillText(`Level: ${gameState.currentLevel}`, 20, 60);
    
    // 渲染剩余步数
    this.ctx.fillText(`Moves: ${gameState.remainingMoves}`, 20, 90);
  }
}