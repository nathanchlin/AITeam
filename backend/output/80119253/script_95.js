// 处理单元格点击
function handleCellClick(event) {
    if (gameOver) return;
    
    const row = parseInt(event.currentTarget.dataset.row);
    const col = parseInt(event.currentTarget.dataset.col);
    
    if (board[row][col] !== EMPTY) {
        updateMessage('该位置已有棋子，请选择其他位置', 'error');
        return;
    }
    
    // 落子
    makeMove(row, col);
}