// 检查是否获胜
function checkWin(row, col) {
    const player = board[row][col];
    
    // 检查四个方向：水平、垂直、对角线、反对角线
    const directions = [
        [{r: 0, c: 1}, {r: 0, c: -1}],  // 水平
        [{r: 1, c: 0}, {r: -1, c: 0}],  // 垂直
        [{r: 1, c: 1}, {r: -1, c: -1}], // 对角线
        [{r: 1, c: -1}, {r: -1, c: 1}]  // 反对角线
    ];
    
    for (const [dir1, dir2] of directions) {
        let count = 1;  // 当前位置已经有一个棋子
        
        // 检查第一个方向
        count += countConsecutive(row, col, dir1[0], dir1[1], player);
        
        // 检查相反方向
        count += countConsecutive(row, col, dir2[0], dir2[1], player);
        
        if (count >= 5) {
            return true;
        }
    }
    
    return false;
}

// 计算连续同色棋子数量
function countConsecutive(row, col, rowDir, colDir, player) {
    let count = 0;
    let r = row + rowDir;
    let c = col + colDir;
    
    while (r >= 0 && r < BOARD_SIZE && c >= 0 && c < BOARD_SIZE && board[r][c] === player) {
        count++;
        r += rowDir;
        c += colDir;
    }
    
    return count;
}