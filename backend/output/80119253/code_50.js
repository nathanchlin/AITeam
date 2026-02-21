// 撤销按钮
const undoButton = document.createElement('button');
undoButton.className = 'control-button';
undoButton.textContent = '撤销';
undoButton.addEventListener('click', undoMove);
document.querySelector('.control-panel').appendChild(undoButton);

// 撤销函数
function undoMove() {
  if (moveHistory.length > 0) {
    const lastMove = moveHistory.pop();
    const cell = document.querySelector(`.cell[data-row="${lastMove.row}"][data-col="${lastMove.col}"]`);
    const piece = cell.querySelector('.piece');
    if (piece) {
      piece.style.transform = 'scale(0)';
      setTimeout(() => piece.remove(), 300);
    }
    currentPlayer = currentPlayer === 'black' ? 'white' : 'black';
    updateStatus();
    playSound('place');
  }
}