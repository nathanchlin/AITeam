function playScoreSound() {
  const scoreSound = new Audio('sounds/score.mp3');
  scoreSound.volume = 0.6;
  scoreSound.play().catch(e => console.log("音频播放失败:", e));
}