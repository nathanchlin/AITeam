// 添加悬停效果
document.querySelectorAll('.cell').forEach(cell => {
  cell.addEventListener('mouseenter', function() {
    if (!this.querySelector('.piece') && !gameOver) {
      const preview = document.createElement('div');
      preview.className = `piece-preview ${currentPlayer === 'black' ? 'black' : 'white'}`;
      preview.style.width = '80%';
      preview.style.height = '80%';
      preview.style.borderRadius = '50%';
      preview.style.position = 'absolute';
      preview.style.top = '10%';
      preview.style.left = '10%';
      preview.style.opacity = '0.5';
      preview.style.pointerEvents = 'none';
      this.appendChild(preview);
    }
  });
  
  cell.addEventListener('mouseleave', function() {
    const preview = this.querySelector('.piece-preview');
    if (preview) {
      preview.remove();
    }
  });
});