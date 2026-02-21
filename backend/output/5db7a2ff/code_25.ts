interface GameState {
    board: number[][];
    score: number;
    gameOver: boolean;
    moveCount: number;
    gridSize: number;
}

class Game2046 {
    private state: GameState;
    private readonly gridSize: number = 4;
    
    constructor() {
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
    
    private initializeBoard(): number[][] {
        return Array(this.gridSize).fill(null).map(() => Array(this.gridSize).fill(0));
    }
}