function playCollisionSound(intensity = 1) {
  const collisionSound = new Audio('sounds/collision.mp3');
  collisionSound.volume = Math.min(1, 0.5 * intensity);
  collisionSound.play().catch(e => console.log("音频播放失败:", e));
}