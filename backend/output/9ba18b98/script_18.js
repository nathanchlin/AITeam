function clearLines(board, linesToClear) {
    // 按从下到上的顺序消除行，避免索引错位
    linesToClear.sort((a, b) => b - a);
    
    // 消除满行并让上面的行下落
    for (const row of linesToClear) {
        board.splice(row, 1); // 移除满行
        board.unshift(new Array(board[0].length).fill(0)); // 在顶部添加新的空行
    }
    
    return linesToClear.length; // 返回消除的行数
}