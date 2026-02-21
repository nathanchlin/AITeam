class GameLogic {
  constructor(gameState) {
    this.gameState = gameState;
    this.matchFinder = new MatchFinder();
    this.animationManager = new AnimationManager();
  }
  
  update() {
    // 1. 检测匹配
    const matches = this.matchFinder.findMatches(this.gameState.grid);
    
    if (matches.length > 0) {
      // 2. 处理匹配
      this.processMatches(matches);
    }
    
    // 3. 应用动画
    this.animationManager.update();
  }
  
  processMatches(matches) {
    // 移除匹配的元素
    matches.forEach(match => {
      match.forEach(cell => {
        this.gameState.grid[cell.row][cell.col] = null;
      });
    });
    
    // 计算得分
    this.gameState.score += this.calculateScore(matches);
    
    // 触发下落和填充
    this.applyGravity();
    this.fillEmptyCells();
  }
  
  calculateScore(matches) {
    // 根据匹配数量计算得分
    let score = 0;
    matches.forEach(match => {
      score += match.length * 10;
    });
    return score;
  }
  
  applyGravity() {
    // 实现下落逻辑
    for (let col = 0; col < this.gameState.grid.width; col++) {
      for (let row = this.gameState.grid.height - 1; row >= 0; row--) {
        if (this.gameState.grid[row][col] === null) {
          // 找到上方最近的非空格子
          for (let searchRow = row - 1; searchRow >= 0; searchRow--) {
            if (this.gameState.grid[searchRow][col] !== null) {
              // 交换位置
              this.gameState.grid[row][col] = this.gameState.grid[searchRow][col];
              this.gameState.grid[searchRow][col] = null;
              break;
            }
          }
        }
      }
    }
  }
  
  fillEmptyCells() {
    // 填充新元素
    for (let col = 0; col < this.gameState.grid.width; col++) {
      for (let row = 0; row < this.gameState.grid.height; row++) {
        if (this.gameState.grid[row][col] === null) {
          this.gameState.grid[row][col] = this.generateRandomElement();
        }
      }
    }
  }
  
  generateRandomElement() {
    // 生成随机元素类型
    const types = ['red', 'blue', 'green', 'yellow', 'purple'];
    return types[Math.floor(Math.random() * types.length)];
  }
}