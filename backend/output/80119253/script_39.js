function initializeGameUI() {
    const gameContainer = document.getElementById('game-container');
    
    // 创建游戏布局
    gameContainer.innerHTML = `
        <div class="game-header">
            <h1>五子棋</h1>
            <div class="timer">
                <span>时间:</span>
                <span id="timer">00:00</span>
            </div>
        </div>
        
        <div class="game-content">
            <div id="status-panel" class="status-panel"></div>
            <div id="game-board" class="game-board"></div>
            <div class="instructions-panel"></div>
        </div>
    `;
    
    // 初始化棋盘
    initializeBoard();
    
    // 渲染状态面板
    document.getElementById('status-panel').appendChild(renderStatusPanel());
    
    // 渲染操作说明
    document.querySelector('.instructions-panel').appendChild(renderInstructions());
    
    // 启动棋盘提示
    showBoardHints();
    
    // 开始计时
    startTimer();
    
    // 显示欢迎消息
    showNotification("欢迎来到五子棋游戏! 黑方先行");
}