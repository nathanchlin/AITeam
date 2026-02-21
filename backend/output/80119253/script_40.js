function bindEvents() {
    // 棋盘点击事件
    document.getElementById('game-board').addEventListener('click', handleBoardClick);
    
    // 窗口失焦时暂停游戏
    window.addEventListener('blur', () => {
        if (gameState.isPlaying) {
            togglePause();
        }
    });
}

function updateUI() {
    // 更新状态面板
    const statusPanel = document.getElementById('status-panel');
    statusPanel.innerHTML = '';
    statusPanel.appendChild(renderStatusPanel());
    
    // 更新棋盘
    updateBoard();
    
    // 更新按钮状态
    updateControlButtons();
}

function updateControlButtons() {
    const pauseBtn = document.getElementById('pause-btn');
    pauseBtn.textContent = gameState.isPlaying ? '暂停' : '继续';
    
    const undoBtn = document.getElementById('undo-btn');
    undoBtn.disabled = gameState.moveHistory.length === 0 || !gameState.isPlaying;
}