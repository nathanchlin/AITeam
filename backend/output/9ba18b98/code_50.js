// 游戏常量
const COLS = 10;
const ROWS = 20;
const BLOCK_SIZE = 30;
const COLORS = [
    '#FF0D72', '#0DC2FF', '#0DFF72', '#F538FF',
    '#FF8E0D', '#FFE138', '#3877FF'
];

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
class Piece {
    constructor() {
        this.type = Math.floor(Math.random() * SHAPES.length);
        this.shape = SHAPES[this.type];
        this.color = COLORS[this.type];
        this.x = Math.floor(COLS / 2) - Math.floor(this.shape[0].length / 2);
        this.y = 0;
    }
    
    // 旋转方块
    rotate() {
        // 创建旋转后的形状
        const rotated = [];
        const rows = this.shape.length;
        const cols = this.shape[0].length;
        
        for (let i = 0; i < cols; i++) {
            rotated[i] = [];
            for (let j = rows - 1; j >= 0; j--) {
                rotated[i][rows - 1 - j] = this.shape[j][i];
            }
        }
        
        // 检查旋转后是否合法
        if (this.isValidMove(this.x, this.y, rotated)) {
            this.shape = rotated;
        }
    }
    
    // 检查移动是否合法
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
    
    // 移动方块
    moveLeft() {
        if (this.isValidMove(this.x - 1, this.y)) {
            this.x--;
        }
    }
    
    moveRight() {
        if (this.isValidMove(this.x + 1, this.y)) {
            this.x++;
        }
    }
    
    moveDown() {
        if (this.isValidMove(this.x, this.y + 1)) {
            this.y++;
            return true;
        }
        return false;
    }
    
    // 硬降落
    hardDrop() {
        while (this.moveDown()) {
            // 继续下落直到不能移动
        }
    }
}

// 游戏变量
let board = Array(ROWS).fill().map(() => Array(COLS).fill(0));
let currentPiece = null;
let score = 0;
let level = 1;
let lines = 0;
let gameRunning = false;
let dropInterval = 1000;
let lastDropTime = 0;

// 初始化游戏
function initGame() {
    board = Array(ROWS).fill().map(() => Array(COLS).fill(0));
    score = 0;
    level = 1;
    lines = 0;
    dropInterval = 1000;
    gameRunning = true;
    
    spawnNewPiece();
    updateScore();
    gameLoop();
}

// 生成新方块
function spawnNewPiece() {
    currentPiece = new Piece();
    
    // 检查游戏是否结束
    if (!currentPiece.isValidMove(currentPiece.x, currentPiece.y)) {
        gameOver();
    }
}

// 游戏主循环
function gameLoop() {
    if (!gameRunning) return;
    
    const now = Date.now();
    
    if (now - lastDropTime > dropInterval) {
        if (!currentPiece.moveDown()) {
            lockPiece();
            clearLines();
            spawnNewPiece();
        }
        lastDropTime = now;
    }
    
    draw();
    requestAnimationFrame(gameLoop);
}

// 锁定方块
function lockPiece() {
    for (let y = 0; y < currentPiece.shape.length; y++) {
        for (let x = 0; x < currentPiece.shape[y].length; x++) {
            if (currentPiece.shape[y][x]) {
                const boardY = currentPiece.y + y;
                const boardX = currentPiece.x + x;
                if (boardY >= 0) {
                    board[boardY][boardX] = currentPiece.color;
                }
            }
        }
    }
}

// 消除完整行
function clearLines() {
    let linesCleared = 0;
    
    for (let y = ROWS - 1; y >= 0; y--) {
        if (board[y].every(cell => cell !== 0)) {
            board.splice(y, 1);
            board.unshift(Array(COLS).fill(0));
            linesCleared++;
            y++; // 重新检查当前行，因为下面的行上移了
        }
    }
    
    if (linesCleared > 0) {
        lines += linesCleared;
        score += linesCleared * 100 * level;
        
        // 每10行提升一个等级
        if (lines >= level * 10) {
            level++;
            dropInterval = Math.max(100, 1000 - (level - 1) * 100);
        }
        
        updateScore();
    }
}

// 更新分数显示
function updateScore() {
    document.getElementById('score').textContent = `分数: ${score}`;
    document.getElementById('level').textContent = `等级: ${level}`;
    document.getElementById('lines').textContent = `行数: ${lines}`;
}

// 游戏结束
function gameOver() {
    gameRunning = false;
    const highScore = localStorage.getItem('tetrisHighScore') || 0;
    
    if (score > highScore) {
        localStorage.setItem('tetrisHighScore', score);
        document.getElementById('highScore').textContent = `最高分: ${score}`;
        alert(`游戏结束！新纪录：${score}分！`);
    } else {
        alert(`游戏结束！得分：${score}`);
    }
}

// 绘制游戏
function draw() {
    const ctx = document.getElementById('gameCanvas').getContext('2d');
    
    // 清空画布
    ctx.clearRect(0, 0, COLS * BLOCK_SIZE, ROWS * BLOCK_SIZE);
    
    // 绘制网格背景
    ctx.strokeStyle = '#333';
    ctx.lineWidth = 0.5;
    
    for (let x = 0; x <= COLS; x++) {
        ctx.beginPath();
        ctx.moveTo(x * BLOCK_SIZE, 0);
        ctx.lineTo(x * BLOCK_SIZE, ROWS * BLOCK_SIZE);
        ctx.stroke();
    }
    
    for (let y = 0; y <= ROWS; y++) {
        ctx.beginPath();
        ctx.moveTo(0, y * BLOCK_SIZE);
        ctx.lineTo(COLS * BLOCK_SIZE, y * BLOCK_SIZE);
        ctx.stroke();
    }
    
    // 绘制已固定的方块
    for (let y = 0; y < ROWS; y++) {
        for (let x = 0; x < COLS; x++) {
            if (board[y][x]) {
                drawBlock(ctx, x, y, board[y][x]);
            }
        }
    }
    
    // 绘制当前方块
    if (currentPiece) {
        for (let y = 0; y < currentPiece.shape.length; y++) {
            for (let x = 0; x < currentPiece.shape[y].length; x++) {
                if (currentPiece.shape[y][x]) {
                    drawBlock(ctx, currentPiece.x + x, currentPiece.y + y, currentPiece.color);
                }
            }
        }
    }
}

// 绘制单个方块
function drawBlock(ctx, x, y, color) {
    ctx.fillStyle = color;
    ctx.fillRect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE - 1, BLOCK_SIZE - 1);
    
    // 添加高光效果
    ctx.fillStyle = 'rgba(255, 255, 255, 0.3)';
    ctx.fillRect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE - 1, 3);
    ctx.fillRect(x * BLOCK_SIZE, y * BLOCK_SIZE, 3, BLOCK_SIZE - 1);
}

// 键盘控制
document.addEventListener('keydown', (e) => {
    if (!gameRunning || !currentPiece) return;
    
    switch (e.key) {
        case 'ArrowLeft':
            currentPiece.moveLeft();
            break;
        case 'ArrowRight':
            currentPiece.moveRight();
            break;
        case 'ArrowDown':
            currentPiece.moveDown();
            break;
        case 'ArrowUp':
            currentPiece.rotate();
            break;
        case ' ':
            currentPiece.hardDrop();
            break;
    }
});

// 触摸控制
document.getElementById('leftBtn').addEventListener('click', () => {
    if (gameRunning && currentPiece) currentPiece.moveLeft();
});

document.getElementById('rightBtn').addEventListener('click', () => {
    if (gameRunning && currentPiece) currentPiece.moveRight();
});

document.getElementById('downBtn').addEventListener('click', () => {
    if (gameRunning && currentPiece) currentPiece.moveDown();
});

document.getElementById('rotateBtn').addEventListener('click', () => {
    if (gameRunning && currentPiece) currentPiece.rotate();
});

// 开始游戏按钮
document.getElementById('startBtn').addEventListener('click', initGame);

// 加载最高分
window.onload = () => {
    const highScore = localStorage.getItem('tetrisHighScore') || 0;
    document.getElementById('highScore').textContent = `最高分: ${highScore}`;
};