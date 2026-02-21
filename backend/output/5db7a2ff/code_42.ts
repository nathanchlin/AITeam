// 在GameStateManager类中添加以下方法

// 检查是否可以移动
  canMove(): boolean {
    // 检查是否有空格
    for (let i = 0; i < this.gameState.gridSize; i++) {
      for (let j = 0; j < this.gameState.gridSize; j++) {
        if (this.gameState.board[i][j] === 0) {
          return true;
        }
      }
    }
    
    // 检查是否有相邻的相同数字
    for (let i = 0; i < this.gameState.gridSize; i++) {
      for (let j = 0; j < this.gameState.gridSize; j++) {
        const current = this.gameState.board[i][j];
        // 检查右侧
        if (j < this.gameState.gridSize - 1 && this.gameState.board[i][j + 1] === current) {
          return true;
        }
        // 检查下方
        if (i < this.gameState.gridSize - 1 && this.gameState.board[i + 1][j] === current) {
          return true;
        }
      }
    }
    
    return false;
  }

  // 添加新方块
  addNewTile(): boolean {
    const emptyCells: [number, number][] = [];
    
    // 找出所有空格
    for (let i = 0; i < this.gameState.gridSize; i++) {
      for (let j = 0; j < this.gameState.gridSize; j++) {
        if (this.gameState.board[i][j] === 0) {
          emptyCells.push([i, j]);
        }
      }
    }
    
    if (emptyCells.length === 0) {
      return false;
    }
    
    // 随机选择一个空格
    const randomIndex = Math.floor(Math.random() * emptyCells.length);
    const [x, y] = emptyCells[randomIndex];
    
    // 90%概率生成2，10%概率生成4
    this.gameState.board[x][y] = Math.random() < 0.9 ? 2 : 4;
    this.saveToStorage();
    return true;
  }

  // 移动方块并合并
  move(direction: 'up' | 'down' | 'left' | 'right'): { moved: boolean; score: number } {
    const board = this.gameState.board;
    let moved = false;
    let score = 0;
    
    // 根据方向处理移动逻辑
    // 这里简化处理，实际实现需要根据2046游戏规则
    // ...
    
    if (moved) {
      this.updateBoard(board);
      this.updateScore(this.gameState.score + score);
    }
    
    return { moved, score };
  }