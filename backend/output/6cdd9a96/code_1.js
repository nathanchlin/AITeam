// 原始代码
gem.addEventListener('click', handleGemClick);

// 修改后
gem.addEventListener('click', handleGemClick);
gem.addEventListener('touchstart', handleGemTouch);
gem.addEventListener('touchend', handleGemTouchEnd);

function handleGemTouch(e) {
  e.preventDefault();
  // 触摸处理逻辑
}