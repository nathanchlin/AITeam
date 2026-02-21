class WinChecker {
  constructor(board) {
    this.board = board;
    this.winLength = 5; // 五子连珠
  }

  checkWin(x, y, player) {
    // 检查横向
    if (this.checkDirection(x, y, player, 1, 0)) return true;
    
    // 检查纵向
    if (this.checkDirection(x, y, player, 0, 1)) return true;
    
    // 检查左上到右下对角线
    if (this.checkDirection(x, y, player, 1, 1)) return true;
    
    // 检查右上到左下对角线
    if (this.checkDirection(x, y, player, 1, -1)) return true;
    
    return false;
  }

  checkDirection(x, y, player, dx, dy) {
    // 检查特定方向是否有连续五个相同棋子
    let count = 1;
    
    // 正向检查
    let i = 1;
    while (i < this.winLength) {
      const newX = x + i * dx;
      const newY = y + i * dy;
      if (!this.board.isValidPosition(newX, newY) || 
          !this.board.hasPiece(newX, newY, player)) {
        break;
      }
      count++;
      i++;
    }
    
    // 反向检查
    i = 1;
    while (i < this.winLength) {
      const newX = x - i * dx;
      const newY = y - i * dy;
      if (!this.board.isValidPosition(newX, newY) || 
          !this.board.hasPiece(newX, newY, player)) {
        break;
      }
      count++;
      i++;
    }
    
    return count >= this.winLength;
  }

  isDraw() {
    // 检查棋盘是否已满且无胜者
    return this.board.isFull() && !this.hasWinner();
  }

  hasWinner() {
    // 检查是否有胜者
    // 可以遍历棋盘所有位置，调用checkWin
  }
}