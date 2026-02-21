class Gomoku {
  constructor() {
    // ... 其他初始化代码 ...
    this.moveHistory = []; // 存储每一步的落子信息
    this.maxUndoSteps = 10; // 最大悔棋步数
  }

  // 在落子时记录历史
  makeMove(row, col) {
    if (this.isValidMove(row, col)) {
      this.board[row][col] = this.currentPlayer;
      this.moveHistory.push({
        row,
        col,
        player: this.currentPlayer,
        boardState: this.board.map(row => [...row]) // 保存当前棋盘状态
      });
      
      // 检查胜利条件
      if (this.checkWin(row, col)) {
        this.gameOver = true;
        this.winner = this.currentPlayer;
      } else {
        this.currentPlayer = this.currentPlayer === 'black' ? 'white' : 'black';
      }
      
      return true;
    }
    return false;
  }

  // 悔棋功能
  undoMove() {
    if (this.moveHistory.length === 0 || this.gameOver) {
      return false;
    }
    
    const lastMove = this.moveHistory.pop();
    this.board = lastMove.boardState; // 恢复棋盘状态
    this.currentPlayer = lastMove.player;
    
    // 如果是悔棋后的一步导致游戏结束，重置游戏结束状态
    if (this.winner) {
      this.gameOver = false;
      this.winner = null;
    }
    
    // 播放悔棋音效
    this.playSound('undo');
    
    return true;
  }
}