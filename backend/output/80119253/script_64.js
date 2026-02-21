function checkWin(board, row, col, player) {
  // 检查四个方向：水平、垂直、对角线、反对角线
  const directions = [
    [[0, 1], [0, -1]],   // 水平
    [[1, 0], [-1, 0]],   // 垂直
    [[1, 1], [-1, -1]],  // 对角线
    [[1, -1], [-1, 1]]   // 反对角线
  ];
  
  for (const direction of directions) {
    let count = 1;
    
    for (const [dx, dy] of direction) {
      let r = row + dx;
      let c = col + dy;
      
      while (r >= 0 && r < 15 && c >= 0 && c < 15 && board[r][c] === player) {
        count++;
        r += dx;
        c += dy;
      }
    }
    
    if (count >= 5) {
      return true;
    }
  }
  
  return false;
}