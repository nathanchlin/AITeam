// 碰撞检测
function collisionDetection() {
    for (let c = 0; c < brickColumnCount; c++) {
        for (let r = 0; r < brickRowCount; r++) {
            const b = bricks[c][r];
            if (b.status === 1) {
                if (
                    ball.x > b.x && 
                    ball.x < b.x + brickWidth && 
                    ball.y > b.y && 
                    ball.y < b.y + brickHeight
                ) {
                    ball.dy = -ball.dy;
                    b.status = 0;
                    score += 10;
                    scoreElement.textContent = score;
                    
                    // 检查是否所有砖块都被消除
                    if (score === brickRowCount * brickColumnCount * 10) {
                        gameWin();
                    }
                }
            }
        }
    }
}