// 完整的Game2046类实现
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
    
    public moveLeft(): boolean {
        if (this.state.gameOver) return false;
        
        let moved = false;
        const newBoard = this.state.board.map(row => [...row]);
        
        for (let i = 0; i < this.gridSize; i++) {
            const row = newBoard[i].filter(val => val !== 0);
            
            for (let j = 0; j < row.length - 1; j++) {
                if (row[j] === row[j + 1]) {
                    row[j] *= 2;
                    this.state.score += row[j];
                    row.splice(j + 1, 1);
                }
            }
            
            while (row.length < this.gridSize) {
                row.push(0);
            }
            
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
    
    public moveRight(): boolean {
        if (this.state.gameOver) return false;
        
        const reversedBoard = this.state.board.map(row => row.reverse());
        this.state.board = reversedBoard;
        const moved = this.moveLeft();
        this.state.board = this.state.board.map(row => row.reverse());
        
        return moved;
    }
    
    public moveUp(): boolean {
        if (this.state.gameOver) return false;
        
        this.transposeBoard();
        const moved = this.moveLeft();
        this.transposeBoard();
        
        return moved;
    }
    
    public moveDown(): boolean {
        if (this.state.gameOver) return false;
        
        this.transposeBoard();
        const moved = this.moveRight();
        this.transposeBoard();
        
        return moved;
    }
    
    private transposeBoard(): void {
        const newBoard = Array(this.gridSize).fill(null).map(() => Array(this.gridSize).fill(0));
        
        for (let i = 0; i < this.gridSize; i++) {
            for (let j = 0; j < this.gridSize; j++) {
                newBoard[j][i] = this.state.board[i][j];
            }
        }
        
        this.state.board = newBoard;
    }
    
    private arraysEqual(a: number[], b: number[]): boolean {
        return a.length === b.length && a.every((val, index) => val === b[index]);
    }
    
    private addRandomTile(): void {
        const emptyCells: [number, number][] = [];
        
        for (let i = 0; i < this.gridSize; i++) {
            for (let j = 0; j < this.gridSize; j++) {
                if (this.state.board[i][j] === 0) {
                    emptyCells.push([i, j]);
                }
            }
        }
        
        if (emptyCells.length > 0) {
            const [randIndex, randCell] = this.getRandomElement(emptyCells);
            const [row, col] = randCell;
            
            this.state.board[row][col] = Math.random() < 0.9 ? 2 : 4;
        }
    }
    
    private getRandomElement<T>(array: T[]): [number, T] {
        const randomIndex = Math.floor(Math.random() * array.length);
        return [randomIndex, array[randomIndex]];
    }
    
    private checkGameOver(): void {
        for (let i = 0; i < this.gridSize; i++) {
            for (let j = 0; j < this.gridSize; j++) {
                if (this.state.board[i][j] === 0) {
                    return;
                }
            }
        }
        
        for (let i = 0; i < this.gridSize; i++) {
            for (let j = 0; j < this.gridSize; j++) {
                const current = this.state.board[i][j];
                
                if (j < this.gridSize - 1 && current === this.state.board[i][j + 1]) {
                    return;
                }
                
                if (i < this.gridSize - 1 && current === this.state.board[i + 1][j]) {
                    return;
                }
            }
        }
        
        this.state.gameOver = true;
    }
    
    public getState(): GameState {
        return {
            ...this.state,
            board: this.state.board.map(row => [...row])
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
    
    public isGameOver(): boolean {
        return this.state.gameOver;
    }
}

// 使用示例
const game = new Game2046();

// 游戏循环示例
function gameLoop() {
    if (game.isGameOver()) {
        console.log("游戏结束! 最终得分:", game.getScore());
        return;
    }
    
    // 这里可以添加用户输入处理
    // 例如：监听键盘事件调用相应的移动方法
    
    // 示例：向左移动
    game.moveLeft();
    
    // 打印当前游戏状态
    const state = game.getState();
    console.log("当前得分:", state.score);
    console.log("移动次数:", state.moveCount);
    console.log("游戏板:");
    state.board.forEach(row => console.log(row.join(" ")));
    
    // 继续游戏循环...
}

// 初始化游戏
console.log("游戏开始!");
gameLoop();