// 使用requestAnimationFrame优化游戏循环
function gameLoop() {
    if (!gameRunning) return;
    
    // 更新游戏状态
    update();
    
    // 渲染游戏
    render();
    
    // 控制游戏速度
    setTimeout(function() {
        requestAnimationFrame(gameLoop);
    }, 100); // 控制速度，可根据设备性能调整
}

// 替换原来的setInterval
// 原代码：setInterval(gameLoop, 100);
// 修复后：
requestAnimationFrame(gameLoop);