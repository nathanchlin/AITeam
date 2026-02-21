function gameLoop() {
    if (!gameState.isRunning) return;
    
    // 清空画布
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // 更新和绘制游戏元素
    // ...
    
    // 继续游戏循环
    requestAnimationFrame(gameLoop);
}