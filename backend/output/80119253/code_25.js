class GomokuGame {
  constructor(boardSize = 15) {
    this.boardSize = boardSize;
    this.board = Array(boardSize).fill(null).map(() => Array(boardSize).fill(0));
    this.currentPlayer = 1; // 1 代表黑棋，2 代表白棋
    this.gameActive = true;
    this.moveHistory = [];
  }

  /**
   * 处理玩家点击棋盘事件
   * @param {number} row - 点击的行索引
   * @param {number} col - 点击的列索引
   * @returns {boolean} 是否成功落子
   */
  handleCellClick(row, col) {
    // 验证游戏是否仍活跃
    if (!this.gameActive) {
      console.log('游戏已结束');
      return false;
    }

    // 验证落子位置是否有效
    if (!this.isValidMove(row, col)) {
      console.log('无效的落子位置');
      return false;
    }

    // 执行落子
    this.makeMove(row, col);
    
    // 检查是否获胜
    if (this.checkWin(row, col)) {
      console.log(`玩家 ${this.currentPlayer === 1 ? '黑棋' : '白棋'} 获胜！`);
      this.gameActive = false;
      return true;
    }

    // 检查是否平局
    if (this.checkDraw()) {
      console.log('游戏平局！');
      this.gameActive = false;
      return true;
    }

    // 切换玩家
    this.switchPlayer();
    return true;
  }

  /**
   * 验证落子位置是否有效
   * @param {number} row - 行索引
   * @param {number} col - 列索引
   * @returns {boolean} 位置是否有效
   */
  isValidMove(row, col) {
    // 检查是否在棋盘范围内
    if (row < 0 || row >= this.boardSize || col < 0 || col >= this.boardSize) {
      return false;
    }

    // 检查位置是否已被占用
    if (this.board[row][col] !== 0) {
      return false;
    }

    return true;
  }

  /**
   * 执行落子操作
   * @param {number} row - 行索引
   * @param {number} col - 列索引
   */
  makeMove(row, col) {
    this.board[row][col] = this.currentPlayer;
    this.moveHistory.push({ row, col, player: this.currentPlayer });
  }

  /**
   * 切换当前玩家
   */
  switchPlayer() {
    this.currentPlayer = this.currentPlayer === 1 ? 2 : 1;
  }

  /**
   * 检查是否获胜
   * @param {number} lastRow - 最后落子的行
   * @param {number} lastCol - 最后落子的列
   * @returns {boolean} 是否获胜
   */
  checkWin(lastRow, lastCol) {
    const directions = [
      [0, 1],  // 水平
      [1, 0],  // 垂直
      [1, 1],  // 对角线（左上到右下）
      [1, -1]  // 对角线（右上到左下）
    ];

    for (const [dx, dy] of directions) {
      let count = 1;  // 包括刚落下的棋子

      // 正方向检查
      for (let i = 1; i < 5; i++) {
        const newRow = lastRow + dx * i;
        const newCol = lastCol + dy * i;
        
        if (this.isInBounds(newRow, newCol) && 
            this.board[newRow][newCol] === this.currentPlayer) {
          count++;
        } else {
          break;
        }
      }

      // 反方向检查
      for (let i = 1; i < 5; i++) {
        const newRow = lastRow - dx * i;
        const newCol = lastCol - dy * i;
        
        if (this.isInBounds(newRow, newCol) && 
            this.board[newRow][newCol] === this.currentPlayer) {
          count++;
        } else {
          break;
        }
      }

      if (count >= 5) {
        return true;
      }
    }

    return false;
  }

  /**
   * 检查是否平局
   * @returns {boolean} 是否平局
   */
  checkDraw() {
    for (let row = 0; row < this.boardSize; row++) {
      for (let col = 0; col < this.boardSize; col++) {
        if (this.board[row][col] === 0) {
          return false;
        }
      }
    }
    return true;
  }

  /**
   * 检查坐标是否在棋盘范围内
   * @param {number} row - 行索引
   * @param {number} col - 列索引
   * @returns {boolean} 是否在范围内
   */
  isInBounds(row, col) {
    return row >= 0 && row < this.boardSize && col >= 0 && col < this.boardSize;
  }

  /**
   * 重置游戏
   */
  resetGame() {
    this.board = Array(this.boardSize).fill(null).map(() => Array(this.boardSize).fill(0));
    this.currentPlayer = 1;
    this.gameActive = true;
    this.moveHistory = [];
  }

  /**
   * 获取当前玩家
   * @returns {number} 当前玩家（1=黑棋，2=白棋）
   */
  getCurrentPlayer() {
    return this.currentPlayer;
  }

  /**
   * 获取棋盘状态
   * @returns {number[][]} 棋盘二维数组
   */
  getBoard() {
    return this.board;
  }
}

// 示例用法
const game = new GomokuGame();

// 模拟玩家点击事件
game.handleCellClick(7, 7); // 黑棋落子
game.handleCellClick(7, 8); // 白棋落子
game.handleCellClick(8, 7); // 黑棋落子
game.handleCellClick(8, 8); // 白棋落子
game.handleCellClick(9, 9); // 黑棋落子