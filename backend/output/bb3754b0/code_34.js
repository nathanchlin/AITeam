// 初始化时从localStorage读取最高分
let highScore = localStorage.getItem('flappyBirdHighScore') || 0;

// 游戏结束时检查是否更新最高分
if (score > highScore) {
    highScore = score;
    localStorage.setItem('flappyBirdHighScore', highScore);
    highScoreElement.textContent = highScore;
    finalHighScoreElement.textContent = highScore;
}