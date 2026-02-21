// 蛇的移动逻辑
function moveSnake() {
  const head = {x: snake[0].x, y: snake[0].y};
  
  // 根据方向移动头部
  switch(direction) {
    case 'UP':
      head.y -= 1;
      break;
    case 'DOWN':
      head.y += 1;
      break;
    case 'LEFT':
      head.x -= 1;
      break;
    case 'RIGHT':
      head.x += 1;
      break;
  }
  
  // 检查碰撞
  if (checkCollision(head)) {
    gameOver();
    return;
  }
  
  snake.unshift(head);
  
  // 检查是否吃到食物
  if (head.x === food.x && head.y === food.y) {
    score++;
    generateFood();
  } else {
    snake.pop();
  }
}