// 假设您有一个棋盘的HTML元素，每个格子都有data-row和data-col属性
document.querySelectorAll('.board-cell').forEach(cell => {
  cell.addEventListener('click', function() {
    const row = parseInt(this.dataset.row);
    const col = parseInt(this.dataset.col);
    
    if (game.handleCellClick(row, col)) {
      // 更新UI显示
      updateBoardUI();
      
      // 显示当前玩家
      document.getElementById('current-player').textContent = 
        game.getCurrentPlayer() === 1 ? '黑棋' : '白棋';
    }
  });
});

function updateBoardUI() {
  const board = game.getBoard();
  const cells = document.querySelectorAll('.board-cell');
  
  cells.forEach(cell => {
    const row = parseInt(cell.dataset.row);
    const col = parseInt(cell.dataset.col);
    const value = board[row][col];
    
    // 清除之前的棋子类
    cell.classList.remove('black', 'white');
    
    // 添加新的棋子类
    if (value === 1) {
      cell.classList.add('black');
    } else if (value === 2) {
      cell.classList.add('white');
    }
  });
}