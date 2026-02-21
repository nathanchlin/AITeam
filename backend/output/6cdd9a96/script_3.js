// 添加事件清理
function cleanupGame() {
  gems.forEach(gem => {
    gem.removeEventListener('click', handleGemClick);
    gem.removeEventListener('touchstart', handleGemTouch);
  });
  // 其他清理工作
}

// 在页面卸载时调用
window.addEventListener('beforeunload', cleanupGame);