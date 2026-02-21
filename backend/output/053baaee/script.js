// 游戏循环
function gameLoop() {
    // 1. 处理输入
    handleInput();
    
    // 2. 更新游戏状态
    updateGame();
    
    // 3. 渲染游戏画面
    renderGame();
    
    // 4. 请求下一帧
    if (!gameOver) {
        requestAnimationFrame(gameLoop);
    }
}

// 游戏状态更新
function updateGame() {
    // 更新玩家坦克
    updatePlayerTank();
    
    // 更新敌方坦克
    updateEnemyTanks();
    
    // 更新子弹
    updateBullets();
    
    // 更新障碍物
    updateObstacles();
    
    // 检测碰撞
    checkCollisions();
    
    // 检查游戏结束条件
    checkGameOverCondition();
}