// 键盘事件监听
document.addEventListener('keydown', (e) => {
  switch (e.key) {
    case 'ArrowUp':
      snake.changeDirection('up');
      break;
    case 'ArrowDown':
      snake.changeDirection('down');
      break;
    case 'ArrowLeft':
      snake.changeDirection('left');
      break;
    case 'ArrowRight':
      snake.changeDirection('right');
      break;
  }
});