// 游戏常量
const COLS = 10;
const ROWS = 20;
const BLOCK_SIZE = 30;
const COLORS = [
    '#FF0D72', '#0DC2FF', '#0DFF72', '#F538FF',
    '#FF8E0D', '#FFE138', '#3877FF'
];

// 游戏状态
const GameState = {
    READY: 'ready',
    PLAYING: 'playing',
    PAUSED: 'paused',
    GAME_OVER: 'game_over'
};

// 方块形状定义
const SHAPES = [
    [[1, 1, 1, 1]], // I
    [[1, 1], [1, 1]], // O
    [[1, 1, 1], [0, 1, 0]], // T
    [[1, 1, 1], [1, 0, 0]], // L
    [[1, 1, 1], [0, 0, 1]], // J
    [[0, 1, 1], [1, 1, 0]], // S
    [[1, 1, 0], [0, 1, 1]]  // Z
];

// 方块类
class Block {
    constructor() {
        this.type = Math.floor(Math.random() * SHAPES.length);
        this.shape = SHAPES[this.type];
        this.color = COLORS[this.type];
        this.x = Math.floor((COLS - this.shape[0].length) / 2);
        this.y = 0;
    }
    
    rotate() {
        const rotated = [];
        const rows = this.shape.length;
        const cols = this.shape[0].length;
        
        for (let i = 0; i < cols; i++) {
            rotated[i] = [];
            for (let j = rows - 1; j >= 0; j--) {
                rotated[i][rows - 1 - j] = this.shape[j][i];
            }
        }
        
        return rotated;
    }
}

// 游戏主类
class Tetris {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.canvas.width = COLS * BLOCK_SIZE;
        this.canvas.height = ROWS * BLOCK_SIZE;
        
        this.board = [];
        this.currentBlock = null;
        this.nextBlock = null;
        this.score = 0;
        this.lines = 0;
        this.level = 1;
        this.dropInterval = 1000; // 初始下落间隔(毫秒)
        this.lastDropTime = 0;
        this.gameState = GameState.READY;
        
        this.initBoard();
        this.bindEvents();
        this.loadHighScore();
    }
    
    initBoard() {
        for (let r = 0; r < ROWS; r++) {
            this.board[r] = [];
            for (let c = 0; c < COLS; c++) {
                this.board[r][c] = 0;
            }
        }
    }
    
    bindEvents() {
        document.addEventListener('keydown', (e) => {
            if (this.gameState !== GameState.PLAYING) return;
            
            switch(e.key) {
                case 'ArrowLeft':
                    this.moveBlock(-1, 0);
                    break;
                case 'ArrowRight':
                    this.moveBlock(1, 0);
                    break;
                case 'ArrowDown':
                    this.moveBlock(0, 1);
                    break;
                case 'ArrowUp':
                    this.rotateCurrentBlock();
                    break;
                case ' ':
                    this.hardDrop();
                    break;
            }
        });
        
        // 触摸控制事件
        document.getElementById('leftBtn').addEventListener('click', () => {
            if (this.gameState === GameState.PLAYING) {
                this.moveBlock(-1, 0);
            }
        });
        
        document.getElementById('rightBtn').addEventListener('click', () => {
            if (this.gameState === GameState.PLAYING) {
                this.moveBlock(1, 0);
            }
        });
        
        document.getElementById('downBtn').addEventListener('click', () => {
            if (this.gameState === GameState.PLAYING) {
                this.moveBlock(0, 1);
            }
        });
        
        document.getElementById('rotateBtn').addEventListener('click', () => {
            if (this.gameState === GameState.PLAYING) {
                this.rotateCurrentBlock();
            }
        });
        
        // 游戏控制按钮
        document.getElementById('startBtn').addEventListener('click', () => {
            this.startGame();
        });
        
        document.getElementById('pauseBtn').addEventListener('click', () => {
            this.togglePause();
        });
        
        document.getElementById('resetBtn').addEventListener('click', () => {
            this.resetGame();
        });
    }
    
    startGame() {
        if (this.gameState === GameState.READY || this.gameState === GameState.GAME_OVER) {
            this.gameState = GameState.PLAYING;
            this.currentBlock = new Block();
            this.nextBlock = new Block();
            this.score = 0;
            this.lines = 0;
            this.level = 1;
            this.dropInterval = 1000;
            this.initBoard();
            this.updateDisplay();
            this.gameLoop();
        }
    }
    
    togglePause() {
        if (this.gameState === GameState.PLAYING) {
            this.gameState = GameState.PAUSED;
        } else if (this.gameState === GameState.PAUSED) {
            this.gameState = GameState.PLAYING;
            this.gameLoop();
        }
    }
    
    resetGame() {
        this.gameState = GameState.READY;
        this.currentBlock = null;
        this.nextBlock = null;
        this.score = 0;
        this.lines = 0;
        this.level = 1;
        this.dropInterval = 1000;
        this.initBoard();
        this.updateDisplay();
        this.draw();
    }
    
    moveBlock(dx, dy) {
        if (!this.currentBlock) return;
        
        this.currentBlock.x += dx;
        this.currentBlock.y += dy;
        
        if (this.collision()) {
            this.currentBlock.x -= dx;
            this.currentBlock.y -= dy;
            
            if (dy > 0) {
                this.placeBlock();
                this.clearLines();
                this.currentBlock = this.nextBlock;
                this.nextBlock = new Block();
                
                if (this.collision()) {
                    this.gameOver();
                }
            }
        }
    }
    
    rotateCurrentBlock() {
        if (!this.currentBlock) return;
        
        const originalShape = this.currentBlock.shape;
        this.currentBlock.shape = this.currentBlock.rotate();
        
        if (this.collision()) {
            this.currentBlock.shape = originalShape;
        }
    }
    
    hardDrop() {
        if (!this.currentBlock) return;
        
        while (!this.collision()) {
            this.currentBlock.y++;
        }
        this.currentBlock.y--;
        this.placeBlock();
        this.clearLines();
        this.currentBlock = this.nextBlock;
        this.nextBlock = new Block();
        
        if (this.collision()) {
            this.gameOver();
        }
    }
    
    collision() {
        if (!this.currentBlock) return false;
        
        for (let r = 0; r < this.currentBlock.shape.length; r++) {
            for (let c = 0; c < this.currentBlock.shape[r].length; c++) {
                if (this.currentBlock.shape[r][c] !== 0) {
                    const newX = this.currentBlock.x + c;
                    const newY = this.currentBlock.y + r;
                    
                    if (newX < 0 || newX >= COLS || newY >= ROWS) {
                        return true;
                    }
                    
                    if (newY >= 0 && this.board[newY][newX] !== 0) {
                        return true;
                    }
                }
            }
        }
        return false;
    }
    
    placeBlock() {
        for (let r = 0; r < this.currentBlock.shape.length; r++) {
            for (let c = 0; c < this.currentBlock.shape[r].length; c++) {
                if (this.currentBlock.shape[r][c] !== 0) {
                    const x = this.currentBlock.x + c;
                    const y = this.currentBlock.y + r;
                    
                    if (y >= 0) {
                        this.board[y][x] = this.currentBlock.type + 1;
                    }
                }
            }
        }
    }
    
    clearLines() {
        let linesCleared = 0;
        
        for (let r = ROWS - 1; r >= 0; r--) {
            if (this.board[r].every(cell => cell !== 0)) {
                this.board.splice(r, 1);
                this.board.unshift(new Array(COLS).fill(0));
                linesCleared++;
                r++; // 重新检查当前行
            }
        }
        
        if (linesCleared > 0) {
            this.lines += linesCleared;
            this.score += linesCleared * 100 * this.level;
            
            // 每清除10行升一级
            if (this.lines >= this.level * 10) {
                this.level++;
                this.dropInterval = Math.max(100, 1000 - (this.level - 1) * 100);
            }
            
            this.updateDisplay();
            this.saveHighScore();
        }
    }
    
    gameOver() {
        this.gameState = GameState.GAME_OVER;
        const highScore = localStorage.getItem('tetrisHighScore') || 0;
        
        if (this.score > highScore) {
            localStorage.setItem('tetrisHighScore', this.score);
            document.getElementById('highScore').textContent = this.score;
        }
        
        // 显示游戏结束信息
        this.ctx.fillStyle = 'rgba(0, 0, 0, 0.75)';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        this.ctx.fillStyle = '#FFF';
        this.ctx.font = '30px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.fillText('游戏结束', this.canvas.width / 2, this.canvas.height / 2 - 30);
        
        this.ctx.font = '20px Arial';
        this.ctx.fillText(`得分: ${this.score}`, this.canvas.width / 2, this.canvas.height / 2 + 10);
        this.ctx.fillText('点击"开始游戏"重新开始', this.canvas.width / 2, this.canvas.height / 2 + 50);
    }
    
    updateDisplay() {
        document.getElementById('score').textContent = this.score;
        document.getElementById('lines').textContent = this.lines;
        document.getElementById('level').textContent = this.level;
        
        // 更新下一个方块预览
        const nextCanvas = document.getElementById('nextCanvas');
        const nextCtx = nextCanvas.getContext('2d');
        nextCanvas.width = 4 * BLOCK_SIZE;
        nextCanvas.height = 4 * BLOCK_SIZE;
        
        nextCtx.fillStyle = '#222';
        nextCtx.fillRect(0, 0, nextCanvas.width, nextCanvas.height);
        
        if (this.nextBlock) {
            nextCtx.fillStyle = this.nextBlock.color;
            const offsetX = (4 - this.nextBlock.shape[0].length) * BLOCK_SIZE / 2;
            const offsetY = (4 - this.nextBlock.shape.length) * BLOCK_SIZE / 2;
            
            for (let r = 0; r < this.nextBlock.shape.length; r++) {
                for (let c = 0; c < this.nextBlock.shape[r].length; c++) {
                    if (this.nextBlock.shape[r][c] !== 0) {
                        nextCtx.fillRect(
                            offsetX + c * BLOCK_SIZE,
                            offsetY + r * BLOCK_SIZE,
                            BLOCK_SIZE - 2,
                            BLOCK_SIZE - 2
                        );
                    }
                }
            }
        }
    }
    
    draw() {
        // 清空画布
        this.ctx.fillStyle = '#111';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // 绘制网格
        this.ctx.strokeStyle = '#333';
        this.ctx.lineWidth = 0.5;
        
        for (let r = 0; r <= ROWS; r++) {
            this.ctx.beginPath();
            this.ctx.moveTo(0, r * BLOCK_SIZE);
            this.ctx.lineTo(this.canvas.width, r * BLOCK_SIZE);
            this.ctx.stroke();
        }
        
        for (let c = 0; c <= COLS; c++) {
            this.ctx.beginPath();
            this.ctx.moveTo(c * BLOCK_SIZE, 0);
            this.ctx.lineTo(c * BLOCK_SIZE, this.canvas.height);
            this.ctx.stroke();
        }
        
        // 绘制已放置的方块
        for (let r = 0; r < ROWS; r++) {
            for (let c = 0; c < COLS; c++) {
                if (this.board[r][c] !== 0) {
                    this.drawBlock(c, r, COLORS[this.board[r][c] - 1]);
                }
            }
        }
        
        // 绘制当前方块
        if (this.currentBlock) {
            this.ctx.fillStyle = this.currentBlock.color;
            for (let r = 0; r < this.currentBlock.shape.length; r++) {
                for (let c = 0; c < this.currentBlock.shape[r].length; c++) {
                    if (this.currentBlock.shape[r][c] !== 0) {
                        this.drawBlock(
                            this.currentBlock.x + c,
                            this.currentBlock.y + r,
                            this.currentBlock.color
                        );
                    }
                }
            }
        }
        
        // 绘制暂停状态
        if (this.gameState === GameState.PAUSED) {
            this.ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
            this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
            
            this.ctx.fillStyle = '#FFF';
            this.ctx.font = '30px Arial';
            this.ctx.textAlign = 'center';
            this.ctx.fillText('游戏暂停', this.canvas.width / 2, this.canvas.height / 2);
        }
    }
    
    drawBlock(x, y, color) {
        this.ctx.fillStyle = color;
        this.ctx.fillRect(
            x * BLOCK_SIZE,
            y * BLOCK_SIZE,
            BLOCK_SIZE - 2,
            BLOCK_SIZE - 2
        );
        
        // 添加高光效果
        this.ctx.fillStyle = 'rgba(255, 255, 255, 0.3)';
        this.ctx.fillRect(
            x * BLOCK_SIZE,
            y * BLOCK_SIZE,
            BLOCK_SIZE - 2,
            4
        );
        this.ctx.fillRect(
            x * BLOCK_SIZE,
            y * BLOCK_SIZE,
            4,
            BLOCK_SIZE - 2
        );
    }
    
    gameLoop(currentTime = 0) {
        if (this.gameState !== GameState.PLAYING) return;
        
        if (currentTime - this.lastDropTime > this.dropInterval) {
            this.moveBlock(0, 1);
            this.lastDropTime = currentTime;
        }
        
        this.draw();
        requestAnimationFrame((time) => this.gameLoop(time));
    }
    
    loadHighScore() {
        const highScore = localStorage.getItem('tetrisHighScore') || 0;
        document.getElementById('highScore').textContent = highScore;
    }
    
    saveHighScore() {
        const highScore = localStorage.getItem('tetrisHighScore') || 0;
        if (this.score > highScore) {
            localStorage.setItem('tetrisHighScore', this.score);
            document.getElementById('highScore').textContent = this.score;
        }
    }
}

// 初始化游戏
document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('gameCanvas');
    const game = new Tetris(canvas);
    
    // 初始绘制
    game.draw();
    
    // 更新初始显示
    game.updateDisplay();
});