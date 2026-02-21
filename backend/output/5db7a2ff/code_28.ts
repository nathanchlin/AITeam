class Game2046 {
    // ... 前面的代码 ...
    
    private checkGameOver(): void {
        // 检查是否有空单元格
        for (let i = 0; i < this.gridSize; i++) {
            for (let j = 0; j < this.gridSize; j++) {
                if (this.state.board[i][j] === 0) {
                    return; // 还有空单元格，游戏未结束
                }
            }
        }
        
        // 检查是否有相邻的相同方块
        for (let i = 0; i < this.gridSize; i++) {
            for (let j = 0; j < this.gridSize; j++) {
                const current = this.state.board[i][j];
                
                // 检查右侧
                if (j < this.gridSize - 1 && current === this.state.board[i][j + 1]) {
                    return; // 有相邻相同方块，游戏未结束
                }
                
                // 检查下方
                if (i < this.gridSize - 1 && current === this.state.board[i + 1][j]) {
                    return; // 有相邻相同方块，游戏未结束
                }
            }
        }
        
        // 没有空单元格且没有相邻相同方块，游戏结束
        this.state.gameOver = true;
    }
    
    public isGameOver(): boolean {
        return this.state.gameOver;
    }
}