setDirection(newDirection) {
  // 防止蛇直接掉头
  if (this.direction.x + newDirection.x === 0 && this.direction.y + newDirection.y === 0) {
    return;
  }
  this.nextDirection = newDirection;
}