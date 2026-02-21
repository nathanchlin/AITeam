function collisionDetection() {
    for (let c = 0; c < brickColumnCount; c++) {
        for (let r = 0; r < brickRowCount; r++) {
            const b = bricks[c][r];
            if (b.status === 1) {
                // 检测球是否与砖块碰撞
                if (ball.x + ball.radius > b.x && 
                    ball.x - ball.radius < b.x + brickWidth && 
                    ball.y + ball.radius > b.y && 
                    ball.y - ball.radius < b.y + brickHeight) {
                    
                    // 计算球中心到砖块各边的距离
                    const ballLeft = ball.x - ball.radius;
                    const ballRight = ball.x + ball.radius;
                    const ballTop = ball.y - ball.radius;
                    const ballBottom = ball.y + ball.radius;
                    
                    const brickLeft = b.x;
                    const brickRight = b.x + brickWidth;
                    const brickTop = b.y;
                    const brickBottom = b.y + brickHeight;
                    
                    // 计算球中心到砖块各边的距离
                    const leftDist = ballRight - brickLeft;
                    const rightDist = brickRight - ballLeft;
                    const topDist = ballBottom - brickTop;
                    const bottomDist = brickBottom - ballTop;
                    
                    // 找出最小距离，确定碰撞方向
                    const minDist = Math.min(leftDist, rightDist, topDist, bottomDist);
                    
                    if (minDist === leftDist || minDist === rightDist) {
                        ball.dx = -ball.dx;
                    } else {
                        ball.dy = -ball.dy;
                    }
                    
                    b.status = 0;
                    score += b.points;
                    scoreElement.textContent = score;
                    
                    // 检查是否所有砖块都被消除
                    if (score === getTotalPoints()) {
                        gameWin();
                    }
                }
            }
        }
    }
}