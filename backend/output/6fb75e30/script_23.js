function playJumpSound() {
  const jumpSound = new Audio('sounds/jump.mp3');
  jumpSound.volume = 0.7;
  jumpSound.play().catch(e => console.log("音频播放失败:", e));
}