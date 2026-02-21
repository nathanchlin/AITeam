// 键盘事件处理
const keys = {};

document.addEventListener('keydown', (e) => {
  keys[e.key] = true;
  
  // 空格键射击
  if (e.key === ' ') {
    player.shoot();
  }
});

document.addEventListener('keyup', (e) => {
  keys[e.key] = false;
});

// 在游戏循环中处理移动
function handleInput() {
  // 玩家移动
  if (keys['w'] || keys['W'] || keys['ArrowUp']) {
    player.move('up');
  }
  if (keys['s'] || keys['S'] || keys['ArrowDown']) {
    player.move('down');
  }
  if (keys['a'] || keys['A'] || keys['ArrowLeft']) {
    player.move('left');
  }
  if (keys['d'] || keys['D'] || keys['ArrowRight']) {
    player.move('right');
  }
}

// 在游戏主循环中调用
function gameLoop() {
  // ... 其他代码 ...
  
  handleInput();
  
  // ... 其他代码 ...
}