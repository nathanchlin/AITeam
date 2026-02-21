class Game2046 {
    // ... 前面的代码 ...
    
    private addRandomTile(): void {
        const emptyCells: [number, number][] = [];
        
        // 找出所有空单元格
        for (let i = 0; i < this.gridSize; i++) {
            for (let j = 0; j < this.gridSize; j++) {
                if (this.state.board[i][j] === 0) {
                    emptyCells.push([i, j]);
                }
            }
        }
        
        if (emptyCells.length > 0) {
            // 随机选择一个空单元格
            const [randIndex, randCell] = this.getRandomElement(emptyCells);
            const [row, col] = randCell;
            
            // 90%概率生成2，10%概率生成4
            this.state.board[row][col] = Math.random() < 0.9 ? 2 : 4;
        }
    }
    
    private getRandomElement<T>(array: T[]): [number, T] {
        const randomIndex = Math.floor(Math.random() * array.length);
        return [randomIndex, array[randomIndex]];
    }
}