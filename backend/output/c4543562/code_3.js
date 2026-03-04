// 假设障碍物是一个矩形，位置在 (obstacleX, obstacleY) 和 (obstacleX + obstacleWidth, obstacleY + obstacleHeight)
const obstacleX = 100;
const obstacleY = 100;
const obstacleWidth = 50;
const obstacleHeight = 50;

function updateCharacterPosition() {
  // ...之前的代码

  // 检测碰撞
  if (characterPosition.x < obstacleX + obstacleWidth &&
      characterPosition.x + 20 > obstacleX &&
      characterPosition.y < obstacleY + obstacleHeight &&
      characterPosition.y + 20 > obstacleY) {
    // 触发碰撞事件，例如增加得分
    score += 10;
  }

  // ...之前的代码
}