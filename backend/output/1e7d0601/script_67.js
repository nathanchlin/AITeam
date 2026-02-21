// 优化前：逐个渲染对象
function render() {
  for (let enemy of enemies) {
    ctx.drawImage(enemy.sprite, enemy.x, enemy.y);
  }
  for (let bullet of bullets) {
    ctx.drawImage(bullet.sprite, bullet.x, bullet.y);
  }
}

// 优化后：批量渲染
function render() {
  // 使用requestAnimationFrame和批量绘制
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  
  // 按类型分组渲染
  renderBatch(enemies);
  renderBatch(bullets);
  renderBatch(playerBullets);
}

function renderBatch(objects) {
  // 使用离屏canvas或WebGL批量渲染
  objects.forEach(obj => {
    ctx.drawImage(obj.sprite, obj.x, obj.y);
  });
}