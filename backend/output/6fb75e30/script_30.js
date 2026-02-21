let comboCount = 0;
let comboTimeout;

function updateCombo() {
  comboCount++;
  
  // 显示连击计数
  const comboElement = document.getElementById('combo');
  comboElement.textContent = `${comboCount}x COMBO!`;
  comboElement.style.animation = 'none';
  setTimeout(() => {
    comboElement.style.animation = 'pulse 0.5s';
  }, 10);
  
  // 连击特效
  if (comboCount >= 3) {
    document.getElementById('game-container').classList.add('combo-glow');
    if (comboCount >= 5) {
      document.getElementById('game-container').classList.add('super-combo');
    }
  }
  
  // 重置连击计时器
  clearTimeout(comboTimeout);
  comboTimeout = setTimeout(() => {
    comboCount = 0;
    document.getElementById('combo').textContent = '';
    document.getElementById('game-container').classList.remove('combo-glow', 'super-combo');
  }, 2000);
}