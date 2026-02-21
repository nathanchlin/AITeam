// 初始化游戏
const canvas = document.getElementById('gameCanvas');
const gridSize = 20;
const renderer = new Renderer(canvas, gridSize);

// 游戏对象
const game = {
  state: 'start', // 'start', 'playing', 'gameOver'
  snake: {
    body: [{x: 10, y: 10}],
    direction: 'right'
  },
  food: {x: 5, y: 5},
  score: 0
};

// 渲染游戏
renderer.render(game);

// 游戏循环
function gameLoop() {
  // 更新游戏逻辑...
  
  // 渲染游戏
  renderer.render(game);
  
  requestAnimationFrame(gameLoop);
}

// 开始游戏循环
gameLoop();