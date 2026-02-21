// 基础游戏循环示例
function gameLoop() {
  update(); // 更新游戏状态
  render(); // 渲染画面
  requestAnimationFrame(gameLoop);
}

// Matter.js集成示例
const engine = Matter.Engine.create();
const world = engine.world;

// 创建火柴人物理体
const stickman = Matter.Bodies.rectangle(x, y, width, height, {
  chamfer: { radius: 5 },
  render: { fillStyle: '#333' }
});