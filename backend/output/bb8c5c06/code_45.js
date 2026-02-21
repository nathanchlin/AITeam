checkFoodCollision(food) {
  const head = this.body[0];
  return head.x === food.x && head.y === food.y;
}