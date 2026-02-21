// 音效管理
const soundEffects = {
  place: new Audio('https://assets.mixkit.co/sfx/preview/mixkit-select-click-1109.mp3'),
  win: new Audio('https://assets.mixkit.co/sfx/preview/mixkit-winning-chimes-2015.mp3'),
  invalid: new Audio('https://assets.mixkit.co/sfx/preview/mixkit-wrong-answer-fail-notification-946.mp3')
};

// 播放音效函数
function playSound(type) {
  soundEffects[type].currentTime = 0;
  soundEffects[type].play().catch(e => console.log('Audio play failed:', e));
}