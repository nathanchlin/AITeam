// 避免在游戏循环中创建临时对象
function gameLoop() {
  // 优化前：每次循环创建新数组
  // const activeEnemies = enemies.filter(e => e.active);
  
  // 优化后：重用数组
  if (!activeEnemies) activeEnemies = [];
  else activeEnemies.length = 0;
  
  enemies.forEach(enemy => {
    if (enemy.active) {
      activeEnemies.push(enemy);
    }
  });
  
  // 使用activeEnemies...
}

// 使用对象避免频繁创建
const tempVector = { x: 0, y: 0 };

function calculateMovement(obj, target) {
  // 重用tempVector而不是每次创建新对象
  tempVector.x = target.x - obj.x;
  tempVector.y = target.y - obj.y;
  
  // 计算距离等...
}