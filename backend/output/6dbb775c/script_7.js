function updateScore(x, y) {
  let surroundedCount = 0;
  // 直接在棋盘数组上操作
  for (let i = -1; i <= 1; i++) {
    for (let j = -1; j <= 1; j++) {
      if (x + i >= 0 && x + i < boardSize && y + j >= 0 && y + j < boardSize) {
        if (board[x + i][y + j] !== currentPlayer) {
          surroundedCount++;
        }
      }
    }
  }
  // 更新得分
  // ...
}