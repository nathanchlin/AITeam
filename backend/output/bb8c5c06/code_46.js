checkCollision() {
  return this.checkWallCollision() || this.checkSelfCollision();
}