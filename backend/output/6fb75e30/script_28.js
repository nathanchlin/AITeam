function collisionEffect() {
  // 屏幕震动效果
  const gameContainer = document.getElementById('game-container');
  gameContainer.style.animation = 'shake 0.3s';
  setTimeout(() => {
    gameContainer.style.animation = '';
  }, 300);
  
  // 火柴人闪烁效果
  const stickFigure = document.getElementById('stick-figure');
  stickFigure.style.filter = 'hue-rotate(0deg) saturate(10)';
  setTimeout(() => {
    stickFigure.style.filter = 'hue-rotate(0deg) saturate(1)';
  }, 200);
}

// 添加CSS动画
const style = document.createElement('style');
style.textContent = `
  @keyframes shake {
    0%, 100% { transform: translateX(0); }
    25% { transform: translateX(-5px); }
    75% { transform: translateX(5px); }
  }
`;
document.head.appendChild(style);