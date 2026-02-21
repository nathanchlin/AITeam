class Game2046 {
    // ... 前面的代码 ...
    
    public getState(): GameState {
        return {
            ...this.state,
            board: this.state.board.map(row => [...row]) // 返回副本，避免外部修改
        };
    }
    
    public resetGame(): void {
        this.state = {
            board: this.initializeBoard(),
            score: 0,
            gameOver: false,
            moveCount: 0,
            gridSize: this.gridSize
        };
        this.addRandomTile();
        this.addRandomTile();
    }
    
    public getScore(): number {
        return this.state.score;
    }
    
    public getMoveCount(): number {
        return this.state.moveCount;
    }
}