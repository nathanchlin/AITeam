// 悔棋
function undoMove() {
    if (moveHistory.length === 0 || gameOver) {
        updateMessage('没有可以悔棋的步骤', 'error');
        return;
    }
    
    const lastMove = moveHistory.pop();
    board[lastMove.row][lastMove.col] = EMPTY;
    currentPlayer = lastMove.player;
    
    renderBoard();
    updatePlayerIndicators();
    updateMessage('');
}