function gameLoop() {
  // 清除画布
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  
  // 更新游戏状态
  updateGame();
  
  // 渲染游戏场景
  renderGame();
  
  // 控制帧率
  setTimeout(() => {
    requestAnimationFrame(gameLoop);
  }, 1000 / FPS);
}