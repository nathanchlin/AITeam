// 游戏主循环
function gameLoop() {
    if (!gameRunning) return;
    
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    drawBricks();
    drawBall();
    drawPaddle();
    collisionDetection();
    ballBoundaryCheck();
    paddleBoundaryCheck();
    
    // 更新球的位置
    ball.x += ball.dx;
    ball.y += ball.dy;
    
    requestAnimationFrame(gameLoop);
}