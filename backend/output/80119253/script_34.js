function renderStatusPanel() {
    const statusPanel = document.createElement('div');
    statusPanel.className = 'status-panel';
    
    statusPanel.innerHTML = `
        <div class="game-status">
            <span class="status-label">当前状态:</span>
            <span class="status-value ${gameState.isPlaying ? 'playing' : 'paused'}">
                ${gameState.isPlaying ? '进行中' : '已暂停'}
            </span>
        </div>
        
        <div class="current-player">
            <span class="status-label">当前玩家:</span>
            <span class="player-indicator ${gameState.currentPlayer}"></span>
            <span>${gameState.currentPlayer === 'black' ? '黑方' : '白方'}</span>
        </div>
        
        <div class="game-info">
            <span class="status-label">回合数:</span>
            <span>${gameState.moveHistory.length}</span>
        </div>
        
        ${gameState.winner ? `
        <div class="winner-announcement">
            <span class="winner-text">游戏结束! ${gameState.winner === 'black' ? '黑方' : '白方'}获胜!</span>
        </div>
        ` : ''}
    `;
    
    return statusPanel;
}