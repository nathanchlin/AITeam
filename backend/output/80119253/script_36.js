function showBoardHints() {
    const boardElement = document.getElementById('game-board');
    
    // 添加悬停提示
    boardElement.addEventListener('mouseover', (e) => {
        if (gameState.isPlaying && !gameState.winner) {
            const cell = e.target.closest('.cell');
            if (cell && !cell.hasChildNodes()) {
                cell.classList.add('hover-hint');
                const previewStone = document.createElement('div');
                previewStone.className = `stone-preview ${gameState.currentPlayer}`;
                cell.appendChild(previewStone);
            }
        }
    });
    
    boardElement.addEventListener('mouseout', (e) => {
        const cell = e.target.closest('.cell');
        if (cell) {
            const preview = cell.querySelector('.stone-preview');
            if (preview) {
                cell.removeChild(preview);
                cell.classList.remove('hover-hint');
            }
        }
    });
}