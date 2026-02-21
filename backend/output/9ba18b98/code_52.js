isValidMove(newX, newY, shape = this.shape) {
    for (let y = 0; y < shape.length; y++) {
        for (let x = 0; x < shape[y].length; x++) {
            if (shape[y][x]) {
                const boardX = newX + x;
                const boardY = newY + y;
                
                // 检查边界
                if (boardX < 0 || boardX >= COLS || boardY >= ROWS) {
                    return false;
                }
                
                // 检查是否与已有方块重叠
                if (boardY >= 0 && board[boardY][boardX]) {
                    return false;
                }
            }
        }
    }
    return true;
}