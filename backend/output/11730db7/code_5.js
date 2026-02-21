class GameState {
  constructor() {
    this.grid = [];
    this.score = 0;
    this.currentLevel = 1;
    this.remainingMoves = 30;
    this.gridSize = { width: 8, height: 8 };
    this.selectedTile = null;
    this.isAnimating = false;
    
    this.initializeGrid();
  }
  
  initializeGrid() {
    // 初始化游戏网格
    for (let row = 0; row < this.gridSize.height; row++) {
      this.grid[row] = [];
      for (let col = 0; col < this.gridSize.width; col++) {
        this.grid[row][col] = this.generateRandomElement();
      }
    }
    
    // 确保初始网格没有匹配
    while (this.hasInitialMatches()) {
      this.shuffleGrid();
    }
  }
  
  generateRandomElement() {
    const types = ['red', 'blue', 'green', 'yellow', 'purple'];
    return types[Math.floor(Math.random() * types.length)];
  }
  
  hasInitialMatches() {
    // 检查是否有初始匹配
    for (let row = 0; row < this.gridSize.height; row++) {
      for (let col = 0; col < this.gridSize.width; col++) {
        const current = this.grid[row][col];
        
        // 检查水平匹配
        if (col < this.gridSize.width - 2) {
          if (current === this.grid[row][col + 1] && current === this.grid[row][col + 2]) {
            return true;
          }
        }
        
        // 检查垂直匹配
        if (row < this.gridSize.height - 2) {
          if (current === this.grid[row + 1][col] && current === this.grid[row + 2][col]) {
            return true;
          }
        }
      }
    }
    return false;
  }
  
  shuffleGrid() {
    // 打乱网格
    for (let row = 0; row < this.gridSize.height; row++) {
      for (let col = 0; col < this.gridSize.width; col++) {
        this.grid[row][col] = this.generateRandomElement();
      }
    }
  }
  
  reset() {
    this.score = 0;
    this.remainingMoves = 30;
    this.selectedTile = null;
    this.isAnimating = false;
    this.initializeGrid();
  }
}