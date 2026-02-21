class GemFallSystem {
  constructor(gameBoard) {
    this.gameBoard = gameBoard;
    this.board = gameBoard.board;
    this.boardElement = gameBoard.boardElement;
    this.scoreElement = gameBoard.scoreElement;
    this.score = 0;
    this.isAnimating = false;
    this.fallSpeed = 300; // 下落动画时间(毫秒)
  }

  /**
   * 处理宝石消除后的下落
   * @param {Array} matchedGems - 需要消除的宝石位置数组
   */
  async handleGemFall(matchedGems) {
    if (this.isAnimating || matchedGems.length === 0) return;
    
    this.isAnimating = true;
    
    // 标记要消除的宝石
    this.markGemsForRemoval(matchedGems);
    
    // 更新分数
    this.updateScore(matchedGems.length);
    
    // 移除匹配的宝石并让上方宝石下落
    await this.removeMatchedGemsAndFall();
    
    // 填充顶部空位
    this.fillEmptySpaces();
    
    // 检查新的匹配
    await this.checkForNewMatches();
    
    this.isAnimating = false;
  }

  /**
   * 标记要消除的宝石
   */
  markGemsForRemoval(matchedGems) {
    matchedGem.forEach(gem => {
      const gemElement = this.boardElement.children[gem.row].children[gem.col];
      gemElement.classList.add('removing');
    });
  }

  /**
   * 移除匹配的宝石并让上方宝石下落
   */
  async removeMatchedGemsAndFall() {
    // 移除匹配的宝石
    for (let col = 0; col < this.board.length; col++) {
      // 从下往上查找空位
      let emptyRow = this.board.length - 1;
      
      for (let row = this.board.length - 1; row >= 0; row--) {
        if (this.board[row][col] === null) {
          // 找到空位，上方的宝石下落
          for (let aboveRow = row - 1; aboveRow >= 0; aboveRow--) {
            if (this.board[aboveRow][col] !== null) {
              // 移动宝石数据
              this.board[emptyRow][col] = this.board[aboveRow][col];
              this.board[aboveRow][col] = null;
              
              // 更新DOM
              this.moveGemToPosition(aboveRow, col, emptyRow, col);
              
              emptyRow--;
            }
          }
        }
      }
    }
    
    // 等待动画完成
    await this.wait(this.fallSpeed);
  }

  /**
   * 移动宝石到新位置并添加动画
   */
  moveGemToPosition(fromRow, fromCol, toRow, toCol) {
    const gemElement = this.boardElement.children[fromRow].children[fromCol];
    gemElement.style.transition = `transform ${this.fallSpeed}ms ease-in-out`;
    
    // 计算移动距离
    const tileSize = this.gameBoard.tileSize;
    const translateY = (toRow - fromRow) * tileSize;
    
    gemElement.style.transform = `translateY(${translateY}px)`;
    
    // 更新数据属性
    gemElement.dataset.row = toRow;
    gemElement.dataset.col = toCol;
    
    // 动画结束后重置样式
    setTimeout(() => {
      gemElement.style.transition = '';
      gemElement.style.transform = '';
      this.boardElement.children[toRow].children[toCol] = gemElement;
    }, this.fallSpeed);
  }

  /**
   * 填充顶部空位
   */
  fillEmptySpaces() {
    for (let col = 0; col < this.board.length; col++) {
      for (let row = 0; row < this.board.length; row++) {
        if (this.board[row][col] === null) {
          // 创建新宝石
          const gemType = this.gameBoard.getRandomGemType();
          this.board[row][col] = gemType;
          
          // 创建DOM元素
          const gemElement = document.createElement('div');
          gemElement.className = 'gem';
          gemElement.dataset.row = row;
          gemElement.dataset.col = col;
          gemElement.dataset.type = gemType;
          
          // 设置初始位置（从顶部开始）
          const tileSize = this.gameBoard.tileSize;
          gemElement.style.position = 'absolute';
          gemElement.style.top = `-${(this.board.length - row) * tileSize}px`;
          gemElement.style.left = `${col * tileSize}px`;
          gemElement.style.width = `${tileSize}px`;
          gemElement.style.height = `${tileSize}px`;
          
          // 添加动画
          setTimeout(() => {
            gemElement.style.transition = `transform ${this.fallSpeed}ms ease-in-out`;
            gemElement.style.transform = `translateY(${(this.board.length - row) * tileSize}px)`;
          }, 10);
          
          // 添加到游戏板
          this.boardElement.children[row].children[col] = gemElement;
          this.boardElement.appendChild(gemElement);
        }
      }
    }
    
    // 等待填充动画完成
    return this.wait(this.fallSpeed);
  }

  /**
   * 检查新的匹配
   */
  async checkForNewMatches() {
    const newMatches = this.gameBoard.findMatches();
    if (newMatches.length > 0) {
      // 递归处理新的匹配
      await this.handleGemFall(newMatches);
    }
  }

  /**
   * 更新分数
   */
  updateScore(matchedCount) {
    // 每个宝石10分，连锁反应有额外加分
    const baseScore = matchedCount * 10;
    const comboBonus = matchedCount > 3 ? (matchedCount - 3) * 5 : 0;
    this.score += baseScore + comboBonus;
    
    if (this.scoreElement) {
      this.scoreElement.textContent = this.score;
    }
  }

  /**
   * 工具函数：等待指定毫秒
   */
  wait(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}