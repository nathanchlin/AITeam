function onCanvasClick(event) {
  const x = Math.floor((event.offsetX - 10) / cellSize);
  const y = Math.floor((event.offsetY - 10) / cellSize);
  if (board[x][y] === null) {
    board[x][y] = currentPlayer;
    currentPlayer = currentPlayer === 'black' ? 'white' : 'black';
    updateScore(x, y);
    saveGameState();
    drawBoard();
  }
}