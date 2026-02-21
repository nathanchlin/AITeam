// 落子动画函数
function placePiece(row, col, isBlack) {
  const cell = document.querySelector(`.cell[data-row="${row}"][data-col="${col}"]`);
  const piece = document.createElement('div');
  
  piece.className = `piece ${isBlack ? 'black' : 'white'}`;
  piece.style.width = '80%';
  piece.style.height = '80%';
  piece.style.borderRadius = '50%';
  piece.style.position = 'absolute';
  piece.style.top = '10%';
  piece.style.left = '10%';
  piece.style.transform = 'scale(0)';
  piece.style.transition = 'transform 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55)';
  
  cell.appendChild(piece);
  
  // 触发动画
  setTimeout(() => {
    piece.style.transform = 'scale(1)';
  }, 10);
}

// 胜利动画
function showWinAnimation(winLine) {
  winLine.forEach(({row, col}) => {
    const cell = document.querySelector(`.cell[data-row="${row}"][data-col="${col}"]`);
    const piece = cell.querySelector('.piece');
    if (piece) {
      piece.style.animation = 'pulse 1s infinite';
    }
  });
}

// 添加脉冲动画CSS
const style = document.createElement('style');
style.textContent = `
  @keyframes pulse {
    0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(255, 215, 0, 0.7); }
    50% { transform: scale(1.05); box-shadow: 0 0 0 10px rgba(255, 215, 0, 0); }
    100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(255, 215, 0, 0); }
  }
`;
document.head.appendChild(style);