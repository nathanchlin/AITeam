function gameOver() {
    gameRunning = false;
    clearInterval(gameLoop);
    
    // 显示游戏结束界面
    finalScoreElement.textContent = score;
    gameOverElement.style.display = 'block';
    
    // 更新按钮状态
    startBtn.disabled = false;
    pauseBtn.disabled = true;
}