// 页面加载动画
window.addEventListener('load', () => {
  const board = document.querySelector('.board');
  board.style.opacity = '0';
  board.style.transform = 'scale(0.8)';
  
  setTimeout(() => {
    board.style.transition = 'all 0.5s ease';
    board.style.opacity = '1';
    board.style.transform = 'scale(1)';
  }, 100);
});

// 重置动画
function resetBoard() {
  const board = document.querySelector('.board');
  board.style.opacity = '0';
  board.style.transform = 'scale(0.8)';
  
  setTimeout(() => {
    initializeBoard();
    board.style.opacity = '1';
    board.style.transform = 'scale(1)';
  }, 300);
}