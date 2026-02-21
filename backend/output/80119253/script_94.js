// 执行落子
function makeMove(row, col) {
    board[row][col] = currentPlayer;
    moveHistory.push({ row, col, player: currentPlayer });
    
    renderBoard();
    
    // 检查胜负
    if (checkWin(row, col)) {
        gameOver = true;
        updateMessage(`${currentPlayer === BLACK ? '黑棋' : '白棋'}获胜！`, 'win');
        undoButton.disabled = true;
        return;
    }
    
    // 检查平局
    if (checkDraw()) {
        gameOver = true;
        updateMessage('游戏平局！', 'win');
        undoButton.disabled = true;
        return;
    }
    
    // 切换玩家
    currentPlayer = currentPlayer === BLACK ? WHITE : BLACK;
    updatePlayerIndicators();
    updateMessage('');
}