// 触觉反馈函数
function hapticFeedback() {
  if ('vibrate' in navigator) {
    // 短震动表示落子
    navigator.vibrate(50);
    // 长震动表示胜利
    if (gameOver) {
      navigator.vibrate([200, 100, 200]);
    }
  }
}