// 主程序入口
document.addEventListener('DOMContentLoaded', () => {
    // 获取画布元素
    const canvas = document.getElementById('gameCanvas');
    canvas.width = 800;
    canvas.height = 600;
    
    // 创建游戏实例
    const game = new Game(canvas);
    
    // 设置按钮事件
    document.getElementById('startBtn').addEventListener('click', () => {
        game.start();
    });
    
    document.getElementById('pauseBtn').addEventListener('click', () => {
        game.pause();
    });
    
    document.getElementById('restartBtn').addEventListener('click', () => {
        game.restart();
    });
    
    // 启动游戏循环
    game.gameLoop();
});