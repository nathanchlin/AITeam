checkCollision(snakeHead) {
    return snakeHead.x === this.position.x && snakeHead.y === this.position.y;
}