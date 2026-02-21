// 检查是否撞到自己（从第二个身体部分开始检查）
for (let i = 1; i < snake.length; i++) {
    if (head.x === snake[i].x && head.y === snake[i].y) {
        return true;
    }
}