// 创建游戏实例
const game = new TetrisGame();

// 游戏主循环
function gameLoop() {
    if (!game.gameOver) {
        game.update();
        game.render();
        requestAnimationFrame(gameLoop);
    }
}

// 开始游戏
gameLoop();