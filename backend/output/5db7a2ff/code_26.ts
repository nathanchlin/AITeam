class Game2046 {
    // ... 前面的代码 ...
    
    // 向左移动
    public moveLeft(): boolean {
        if (this.state.gameOver) return false;
        
        let moved = false;
        const newBoard = this.state.board.map(row => [...row]);
        
        for (let i = 0; i < this.gridSize; i++) {
            // 移除零值
            const row = newBoard[i].filter(val => val !== 0);
            
            // 合并相同的值
            for (let j = 0; j < row.length - 1; j++) {
                if (row[j] === row[j + 1]) {
                    row[j] *= 2;
                    this.state.score += row[j];
                    row.splice(j + 1, 1);
                }
            }
            
            // 填充零值
            while (row.length < this.gridSize) {
                row.push(0);
            }
            
            // 检查是否有移动
            if (!moved && !this.arraysEqual(newBoard[i], row)) {
                moved = true;
            }
            
            newBoard[i] = row;
        }
        
        if (moved) {
            this.state.board = newBoard;
            this.state.moveCount++;
            this.addRandomTile();
            this.checkGameOver();
        }
        
        return moved;
    }
    
    // 向右移动
    public moveRight(): boolean {
        if (this.state.gameOver) return false;
        
        // 翻转每行，向左移动，再翻转回来
        const reversedBoard = this.state.board.map(row => row.reverse());
        this.state.board = reversedBoard;
        const moved = this.moveLeft();
        this.state.board = this.state.board.map(row => row.reverse());
        
        return moved;
    }
    
    // 向上移动
    public moveUp(): boolean {
        if (this.state.gameOver) return false;
        
        // 转置矩阵，向左移动，再转置回来
        this.transposeBoard();
        const moved = this.moveLeft();
        this.transposeBoard();
        
        return moved;
    }
    
    // 向下移动
    public moveDown(): boolean {
        if (this.state.gameOver) return false;
        
        // 转置矩阵，向右移动，再转置回来
        this.transposeBoard();
        const moved = this.moveRight();
        this.transposeBoard();
        
        return moved;
    }
    
    // 辅助方法：转置矩阵
    private transposeBoard(): void {
        const newBoard = Array(this.gridSize).fill(null).map(() => Array(this.gridSize).fill(0));
        
        for (let i = 0; i < this.gridSize; i++) {
            for (let j = 0; j < this.gridSize; j++) {
                newBoard[j][i] = this.state.board[i][j];
            }
        }
        
        this.state.board = newBoard;
    }
    
    // 辅助方法：比较两个数组是否相等
    private arraysEqual(a: number[], b: number[]): boolean {
        return a.length === b.length && a.every((val, index) => val === b[index]);
    }
}