checkWallCollision() {
  const head = this.body[0];
  return head.x < 0 || head.x >= GRID_SIZE || head.y < 0 || head.y >= GRID_SIZE;
}