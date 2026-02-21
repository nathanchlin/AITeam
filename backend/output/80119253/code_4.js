class GameStateManager {
  constructor() {
    this.state = 'waiting'; // waiting, playing, paused, ended
    this.board = new Board(15); // 15x15棋盘
    this.moveValidator = new MoveValidator(this.board);
    this.winChecker = new WinChecker(this.board);
    this.moveHistory = [];
    this.currentPlayer = 'black';
  }

  startGame() {
    this.state = 'playing';
    this.reset();
  }

  reset() {
    this.board.reset();
    this.moveHistory = [];
    this.currentPlayer = 'black';
    this.state = 'playing';
  }

  makeMove(x, y) {
    if (this.state !== 'playing') {
      return false;
    }
    
    if (!this.moveValidator.makeMove(x, y)) {
      return false;
    }
    
    // 记录移动历史
    this.moveHistory.push({x, y, player: this.currentPlayer});
    
    // 检查胜负
    if (this.winChecker.checkWin(x, y, this.currentPlayer)) {
      this.state = 'ended';
      return true;
    }
    
    // 检查平局
    if (this.winChecker.isDraw()) {
      this.state = 'ended';
      return true;
    }
    
    return true;
  }

  undoMove() {
    if (this.moveHistory.length === 0 || this.state !== 'playing') {
      return false;
    }
    
    const lastMove = this.moveHistory.pop();
    this.board.removePiece(lastMove.x, lastMove.y);
    this.moveValidator.switchPlayer();
    return true;
  }

  getState() {
    return {
      state: this.state,
      currentPlayer: this.currentPlayer,
      board: this.board.getState(),
      moveCount: this.moveHistory.length
    };
  }
}