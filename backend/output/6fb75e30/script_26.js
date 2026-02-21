let bgMusic = new Audio('sounds/background.mp3');
bgMusic.loop = true;
bgMusic.volume = 0.25;

function toggleBackgroundMusic(play) {
  if (play) {
    bgMusic.play().catch(e => console.log("背景音乐播放失败:", e));
  } else {
    bgMusic.pause();
  }
}