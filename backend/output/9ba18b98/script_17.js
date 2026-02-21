function checkLines(board) {
    const linesToClear = [];
    
    // 遍历每一行
    for (let row = 0; row < board.length; row++) {
        // 检查该行是否已满
        if (board[row].every(cell => cell !== 0)) {
            linesToClear.push(row);
        }
    }
    
    return linesToClear;
}