// 在 ScoreSystem 类中添加
animateScoreChange() {
  if (this.scoreElement) {
    this.scoreElement.style.transform = 'scale(1.2)';
    this.scoreElement.style.transition = 'transform 0.2s';
    
    setTimeout(() => {
      this.scoreElement.style.transform = 'scale(1)';
    }, 200);
  }
}

// 修改 increaseScore 方法
increaseScore() {
  this.currentScore++;
  this.updateScoreDisplay();
  this.animateScoreChange();
  
  // 检查是否创造新纪录
  if (this.currentScore > this.highScore) {
    this.highScore = this.currentScore;
    this.saveHighScore();
    this.updateHighScoreDisplay();
    // 可以添加新纪录特效
  }
}