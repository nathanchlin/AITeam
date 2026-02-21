// 球边界检测
function ballBoundaryCheck() {
    // 左右边界
    if (ball.x + ball.dx > canvas.width - ball.radius || ball.x + ball.dx < ball.radius) {
        ball.dx = -ball.dx;
    }
    
    // 上边界
    if (ball.y + ball.dy < ball.radius) {
        ball.dy = -ball.dy;
    }
    // 下边界（球掉落）
    else if (ball.y + ball.dy > canvas.height - ball.radius) {
        // 检查是否碰到挡板
        if (ball.x > paddle.x && ball.x < paddle.x + paddle.width) {
            // 根据球击中挡板的位置调整反弹角度
            const hitPos = (ball.x - paddle.x) / paddle.width;
            ball.dx = 8 * (hitPos - 0.5); // -4 到 4 之间的值
            ball.dy = -ball.dy;
        } else {
            // 没有碰到挡板，失去一条生命
            lives--;
            livesElement.textContent = lives;
            
            if (lives === 0) {
                gameOver();
            } else {
                resetBall();
            }
        }
    }
}