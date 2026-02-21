function checkCollision(obj1, obj2) {
  // 矩形碰撞检测
  return obj1.x < obj2.x + obj2.width &&
         obj1.x + obj1.width > obj2.x &&
         obj1.y < obj2.y + obj2.height &&
         obj1.y + obj1.height > obj2.y;
}

function checkBulletCollision(bullet, target) {
  // 子弹与目标碰撞检测
  if (checkCollision(bullet, target)) {
    handleHit(bullet, target);
    return true;
  }
  return false;
}