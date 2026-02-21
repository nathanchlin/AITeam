class UserInterface {
  constructor(gameStateManager, boardRenderer) {
    this.gameStateManager = gameStateStateManager;
    this.boardRenderer = boardRenderer;
    this.initEventListeners();
  }

  initEventListeners() {
    // 棋盘点击事件
    this.boardRenderer.canvas.addEventListener('click', (e) => {
      const rect = this.boardRenderer.canvas.getBoundingClientRect();
      const x = Math.floor((e.clientX - rect.left) / this.boardRenderer.cellSize);
      const y = Math.floor((e.clientY - rect.top) / this.boardRenderer.cellSize);
      
      this.handleBoardClick(x, y);
    });
    
    // 撤销按钮事件
    document.getElementById('undo-button').addEventListener('click', () => {
      this.handleUndo();
    });
    
    // 重新开始按钮事件
    document.getElementById('restart-button').addEventListener('click', () => {
      this.handleRestart();
    });
  }

  handleBoardClick(x, y) {
    if (this.gameStateManager.makeMove(x, y)) {
      this.boardRenderer.renderPiece(x, y, this.gameStateManager.currentPlayer);
      
      if (this.gameStateManager.state === 'ended') {
        this.handleGameEnd();
      }
    }
  }

  handleUndo() {
    if (this.gameStateManager.undoMove()) {
      this.boardRenderer.redraw();
    }
  }

  handleRestart() {
    this.gameStateManager.startGame();
    this.boardRenderer.redraw();
  }

  handleGameEnd() {
    const winner = this.gameStateManager.currentPlayer === 'black' ? '白棋' : '黑棋';
    this.showGameResult(`游戏结束！${winner}获胜！`);
  }

  showGameResult(message) {
    // 显示游戏结果
    const resultElement = document.getElementById('game-result');
    resultElement.textContent = message;
    resultElement.style.display = 'block';
  }
}