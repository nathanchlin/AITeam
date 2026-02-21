class MoveValidator {
  constructor(board) {
    this.board = board;
    this.currentPlayer = 'black'; // 黑棋先行
  }

  isValidMove(x, y) {
    // 检查坐标是否在棋盘范围内
    // 检查该位置是否已有棋子
    return x >= 0 && x < this.board.size && 
           y >= 0 && y < this.board.size && 
           !this.board.isOccupied(x, y);
  }

  makeMove(x, y) {
    if (!this.isValidMove(x, y)) {
      return false;
    }
    
    this.board.placePiece(x, y, this.currentPlayer);
    this.switchPlayer();
    return true;
  }

  switchPlayer() {
    this.currentPlayer = this.currentPlayer === 'black' ? 'white' : 'black';
  }
}