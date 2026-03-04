function drawPiece(x, y, color) {
  const offset = 10;
  const pieceSize = cellSize - 2 * offset;
  const startX = x * cellSize + offset;
  const startY = y * cellSize + offset;
  ctx.fillStyle = color;
  ctx.beginPath();
  ctx.arc(startX + pieceSize / 2, startY + pieceSize / 2, pieceSize / 2 - 2, 0, 2 * Math.PI);
  ctx.fill();
}

function drawBoard() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = 'black';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  // 只重绘棋子
  for (let i = 0; i < boardSize; i++) {
    for (let j = 0; j < boardSize; j++) {
      if (board[i][j]) {
        drawPiece(i, j, board[i][j]);
      }
    }
  }
}