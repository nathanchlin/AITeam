function restartGame() {
    // 清空棋盘
    board = Array(BOARD_SIZE).fill(null).map(() => Array(BOARD_SIZE).fill(null));
    
    // 重置游戏状态
    currentPlayer = PLAYER_BLACK;
    gameOver = false;
    winner = null;
    moveCount = 0;
    
    // 更新UI
    updateBoard();
    updateGameStatus();
    clearMoveHistory();
    
    // 显示重新开始提示
    showNotification("游戏已重新开始，黑方先行");
}