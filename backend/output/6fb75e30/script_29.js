function showScoreAnimation(points, x, y) {
  // 创建浮动分数元素
  const scoreElement = document.createElement('div');
  scoreElement.className = 'floating-score';
  scoreElement.textContent = `+${points}`;
  scoreElement.style.left = `${x}px`;
  scoreElement.style.top = `${y}px`;
  document.getElementById('game-container').appendChild(scoreElement);
  
  // 动画
  scoreElement.animate([
    { transform: 'translateY(0)', opacity: 1 },
    { transform: 'translateY(-50px)', opacity: 0 }
  ], {
    duration: 1000,
    easing: 'ease-out'
  }).onfinish = () => scoreElement.remove();
  
  // 粒子效果
  createParticleEffect(x, y);
}

function createParticleEffect(x, y) {
  for (let i = 0; i < 10; i++) {
    const particle = document.createElement('div');
    particle.className = 'particle';
    particle.style.left = `${x}px`;
    particle.style.top = `${y}px`;
    document.getElementById('game-container').appendChild(particle);
    
    const angle = (Math.PI * 2 * i) / 10;
    const velocity = 50 + Math.random() * 50;
    
    particle.animate([
      { transform: 'translate(0, 0)', opacity: 1 },
      { 
        transform: `translate(${Math.cos(angle) * velocity}px, ${Math.sin(angle) * velocity}px)`, 
        opacity: 0 
      }
    ], {
      duration: 800,
      easing: 'ease-out'
    }).onfinish = () => particle.remove();
  }
}