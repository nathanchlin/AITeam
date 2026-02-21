checkFoodCollision(foodPosition) {
    const head = this.body[0];
    return head.x === foodPosition.x && head.y === foodPosition.y;
}