# AI对手算法实现

**Agent**: coder

**Time**: 2026-02-19T15:58:57.575908

---

我将为您开发一个完整的俄罗斯方块对战游戏，包含AI对手的实现。以下是完整的单文件HTML代码：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>俄罗斯方块对战</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Arial', sans-serif;
            background-color: #1a1a2e;
            color: #eee;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            overflow: hidden;
        }
        
        .game-container {
            display: flex;
            gap: 30px;
            padding: 20px;
            background-color: #16213e;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.5);
        }
        
        .game-board {
            position: relative;
        }
        
        canvas {
            background-color: #0f3460;
            border: 2px solid #e94560;
            border-radius: 5px;
        }
        
        .game-info {
            display: flex;
            flex-direction: column;
            gap: 20px;
            width: 200px;
        }
        
        .info-panel {
            background-color: #0f3460;
            padding: 15px;
            border-radius: 5px;
            border: 1px solid #e94560;
        }
        
        .info-panel h3 {
            margin-bottom: 10px;
            color: #e94560;
        }
        
        .controls {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        
        button {
            background-color: #e94560;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            transition: background-color 0.3s;
        }
        
        button:hover {
            background-color: #c13651;
        }
        
        button:disabled {
            background-color: #555;
            cursor: not-allowed;
        }
        
        .difficulty-selector {
            display: flex;
            flex-direction: column;
            gap: 5px;
        }
        
        .difficulty-selector label {
            display: flex;
            align-items: center;
            gap: 5px;
        }
        
        input[type="radio"] {
            margin-right: 5px;
        }
        
        .score-display {
            font-size: 24px;
            font-weight: bold;
            text-align: center;
            margin: 10px 0;
        }
        
        .next-piece {
            display: flex;
            justify-content: center;
            margin-top: 10px;
        }
        
        .next-piece canvas {
            border: 1px solid #e94560;
        }
        
        .game-over {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background-color: rgba(0, 0, 0, 0.8);
            padding: 30px;
            border-radius: 10px;
            text-align: center;
            display: none;
        }
        
        .game-over h2 {
            color: #e94560;
            margin-bottom: 20px;
        }
        
        .controls-info {
            font-size: 14px;
            line-height: 1.5;
        }
        
        .controls-info kbd {
            background-color: #333;
            padding: 2px 5px;
            border-radius: 3px;
            border: 1px solid #555;
            margin: 0 2px;
        }
    </style>
</head>
<body>
    <div class="game-container">
        <div class="game-board">
            <canvas id="playerCanvas" width="300" height="600"></canvas>
            <div class="game-over" id="playerGameOver">
                <h2>游戏结束</h2>
                <p>最终得分: <span id="playerFinalScore">0</span></p>
                <button id="restartPlayerBtn">重新开始</button>
            </div>
        </div>
        
        <div class="game-info">
            <div class="info-panel">
                <h3>玩家信息</h3>
                <div class="score-display" id="playerScore">0</div>
                <div class="next-piece">
                    <canvas id="playerNextPiece" width="80" height="80"></canvas>
                </div>
                <div class="level-display" style="text-align: center; margin-top: 10px;">
                    等级: <span id="playerLevel">1</span>
                </div>
            </div>
            
            <div class="info-panel">
                <h3>AI对手</h3>
                <div class="score-display" id="aiScore">0</div>
                <div class="next-piece">
                    <canvas id="aiNextPiece" width="80" height="80"></canvas>
                </div>
                <div class="level-display" style="text-align: center; margin-top: 10px;">
                    等级: <span id="aiLevel">1</span>
                </div>
            </div>
            
            <div class="info-panel">
                <h3>游戏控制</h3>
                <div class="controls">
                    <button id="startBtn">开始游戏</button>
                    <button id="pauseBtn" disabled>暂停</button>
                    <button id="restartBtn">重新开始</button>
                </div>
            </div>
            
            <div class="info-panel">
                <h3>AI难度</h3>
                <div class="difficulty-selector">
                    <label>
                        <input type="radio" name="difficulty" value="easy" checked>
                        简单
                    </label>
                    <label>
                        <input type="radio" name="difficulty" value="medium">
                        中等
                    </label>
                    <label>
                        <input type="radio" name="difficulty" value="hard">
                        困难
                    </label>
                </div>
            </div>
            
            <div class="info-panel">
                <h3>操作说明</h3>
                <div class="controls-info">
                    <p><kbd>←</kbd> <kbd>→</kbd> 左右移动</p>
                    <p><kbd>↓</kbd> 加速下落</p>
                    <p><kbd>↑</kbd> 旋转方块</p>
                    <p><kbd>空格</kbd> 直接落下</p>
                </div>
            </div>
        </div>
        
        <div class="game-board">
            <canvas id="aiCanvas" width="300" height="600"></canvas>
            <div class="game-over" id="aiGameOver">
                <h2>AI游戏结束</h2>
                <p>最终得分: <span id="aiFinalScore">0</span></p>
                <button id="restartAiBtn">重新开始</button>
            </div>
        </div>
    </div>

    <script>
        // 游戏常量
        const COLS = 10;
        const ROWS = 20;
        const BLOCK_SIZE = 30;
        
        // 方块形状定义
        const SHAPES = [
            // I
            [[1, 1, 1, 1]],
            // O
            [[1, 1],
             [1, 1]],
            // T
            [[0, 1, 0],
             [1, 1, 1]],
            // S
            [[0, 1, 1],
             [1, 1, 0]],
            // Z
            [[1, 1, 0],
             [0, 1, 1]],
            // J
            [[1, 0, 0],
             [1, 1, 1]],
            // L
            [[0, 0, 1],
             [1, 1, 1]]
        ];
        
        // 方块颜色
        const COLORS = [
            '#00f0f0', // I - 青色
            '#f0f000', // O - 黄色
            '#a000f0', // T - 紫色
            '#00f000', // S - 绿色
            '#f00000', // Z - 红色
            '#0000f0', // J - 蓝色
            '#f0a000'  // L - 橙色
        ];
        
        // 游戏状态
        class GameState {
            constructor(canvas, nextPieceCanvas) {
                this.canvas = canvas;
                this.ctx = canvas.getContext('2d');
                this.nextPieceCanvas = nextPieceCanvas;
                this.nextPieceCtx = nextPieceCanvas.getContext('2d');
                
                this.board = this.createBoard();
                this.currentPiece = null;
                this.nextPiece = null;
                this.score = 0;
                this.level = 1;
                this.lines = 0;
                this.gameOver = false;
                this.paused = false;
                
                this.dropCounter = 0;
                this.dropInterval = 1000; // 初始下落间隔（毫秒）
                this.lastTime = 0;
                
                this.init();
            }
            
            createBoard() {
                return Array(ROWS).fill().map(() => Array(COLS).fill(0));
            }
            
            init() {
                this.spawnPiece();
                this.draw();
            }
            
            spawnPiece() {
                if (!this.nextPiece) {
                    this.nextPiece = this.getRandomPiece();
                }
                
                this.currentPiece = this.nextPiece;
                this.nextPiece = this.getRandomPiece();
                
                // 检查游戏是否结束
                if (this.collision()) {
                    this.gameOver = true;
                    return false;
                }
                
                this.drawNextPiece();
                return true;
            }
            
            getRandomPiece() {
                const typeId = Math.floor(Math.random() * SHAPES.length);
                return {
                    shape: SHAPES[typeId],
                    color: COLORS[typeId],
                    x: Math.floor(COLS / 2) - Math.floor(SHAPES[typeId][0].length / 2),
                    y: 0,
                    typeId: typeId
                };
            }
            
            collision() {
                for (let y = 0; y < this.currentPiece.shape.length; y++) {
                    for (let x = 0; x < this.currentPiece.shape[y].length; x++) {
                        if (this.currentPiece.shape[y][x] !== 0) {
                            const boardX = this.currentPiece.x + x;
                            const boardY = this.currentPiece.y + y;
                            
                            if (boardX < 0 || boardX >= COLS || boardY >= ROWS) {
                                return true;
                            }
                            
                            if (boardY >= 0 && this.board[boardY][boardX] !== 0) {
                                return true;
                            }
                        }
                    }
                }
                return false;
            }
            
            merge() {
                for (let y = 0; y < this.currentPiece.shape.length; y++) {
                    for (let x = 0; x < this.currentPiece.shape[y].length; x++) {
                        if (this.currentPiece.shape[y][x] !== 0) {
                            const boardY = this.currentPiece.y + y;
                            const boardX = this.currentPiece.x + x;
                            if (boardY >= 0) {
                                this.board[boardY][boardX] = this.currentPiece.color;
                            }
                        }
                    }
                }
            }
            
            clearLines() {
                let linesCleared = 0;
                
                for (let y = ROWS - 1; y >= 0; y--) {
                    if (this.board[y].every(cell => cell !== 0)) {
                        this.board.splice(y, 1);
                        this.board.unshift(Array(COLS).fill(0));
                        linesCleared++;
                        y++; // 重新检查当前行
                    }
                }
                
                if (linesCleared > 0) {
                    this.lines += linesCleared;
                    this.score += [40, 100, 300, 1200][linesCleared - 1] * this.level;
                    this.level = Math.floor(this.lines / 10) + 1;
                    this.dropInterval = Math.max(100, 1000 - (this.level - 1) * 100);
                }
                
                return linesCleared;
            }
            
            move(dir) {
                this.currentPiece.x += dir;
                if (this.collision()) {
                    this.currentPiece.x -= dir;
                    return false;
                }
                return true;
            }
            
            rotate() {
                const rotated = this.currentPiece.shape[0].map((_, i) =>
                    this.currentPiece.shape.map(row => row[i]).reverse()
                );
                
                const previousShape = this.currentPiece.shape;
                this.currentPiece.shape = rotated;
                
                if (this.collision()) {
                    this.currentPiece.shape = previousShape;
                    return false;
                }
                return true;
            }
            
            drop() {
                this.currentPiece.y++;
                if (this.collision()) {
                    this.currentPiece.y--;
                    this.merge();
                    const linesCleared = this.clearLines();
                    this.spawnPiece();
                    return linesCleared;
                }
                this.dropCounter = 0;
                return 0;
            }
            
            hardDrop() {
                let linesCleared = 0;
                while (!this.collision()) {
                    this.currentPiece.y++;
                }
                this.currentPiece.y--;
                this.merge();
                linesCleared = this.clearLines();
                this.spawnPiece();
                return linesCleared;
            }
            
            draw() {
                // 清空画布
                this.ctx.fillStyle = '#0f3460';
                this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
                
                // 绘制网格
                this.ctx.strokeStyle = '#1a5490';
                this.ctx.lineWidth = 0.5;
                
                for (let i = 1; i < COLS; i++) {
                    this.ctx.beginPath();
                    this.ctx.moveTo(i * BLOCK_SIZE, 0);
                    this.ctx.lineTo(i * BLOCK_SIZE, this.canvas.height);
                    this.ctx.stroke();
                }
                
                for (let i = 1; i < ROWS; i++) {
                    this.ctx.beginPath();
                    this.ctx.moveTo(0, i * BLOCK_SIZE);
                    this.ctx.lineTo(this.canvas.width, i * BLOCK_SIZE);
                    this.ctx.stroke();
                }
                
                // 绘制已固定的方块
                for (let y = 0; y < ROWS; y++) {
                    for (let x = 0; x < COLS; x++) {
                        if (this.board[y][x]) {
                            this.drawBlock(x, y, this.board[y][x]);
                        }
                    }
                }
                
                // 绘制当前方块
                if (this.currentPiece) {
                    for (let y = 0; y < this.currentPiece.shape.length; y++) {
                        for (let x = 0; x < this.currentPiece.shape[y].length; x++) {
                            if (this.currentPiece.shape[y][x]) {
                                this.drawBlock(
                                    this.currentPiece.x + x,
                                    this.currentPiece.y + y,
                                    this.currentPiece.color
                                );
                            }
                        }
                    }
                }
            }
            
            drawBlock(x, y, color) {
                this.ctx.fillStyle = color;
                this.ctx.fillRect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE);
                
                // 添加高光效果
                this.ctx.fillStyle = 'rgba(255, 255, 255, 0.3)';
                this.ctx.fillRect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, 5);
                this.ctx.fillRect(x * BLOCK_SIZE, y * BLOCK_SIZE, 5, BLOCK_SIZE);
                
                // 添加阴影效果
                this.ctx.fillStyle = 'rgba(0, 0, 0, 0.3)';
                this.ctx.fillRect(x * BLOCK_SIZE + BLOCK_SIZE - 5, y * BLOCK_SIZE, 5, BLOCK_SIZE);
                this.ctx.fillRect(x * BLOCK_SIZE, y * BLOCK_SIZE + BLOCK_SIZE - 5, BLOCK_SIZE, 5);
            }
            
            drawNextPiece() {
                // 清空画布
                this.nextPieceCtx.fillStyle = '#0f3460';
                this.nextPieceCtx.fillRect(0, 0, this.nextPieceCanvas.width, this.nextPieceCanvas.height);
                
                if (!this.nextPiece) return;
                
                const blockSize = 20;
                const offsetX = (this.nextPieceCanvas.width - this.nextPiece.shape[0].length * blockSize) / 2;
                const offsetY = (this.nextPieceCanvas.height - this.nextPiece.shape.length * blockSize) / 2;
                
                for (let y = 0; y < this.nextPiece.shape.length; y++) {
                    for (let x = 0; x < this.nextPiece.shape[y].length; x++) {
                        if (this.nextPiece.shape[y][x]) {
                            this.nextPieceCtx.fillStyle = this.nextPiece.color;
                            this.nextPieceCtx.fillRect(
                                offsetX + x * blockSize,
                                offsetY + y * blockSize,
                                blockSize,
                                blockSize
                            );
                            
                            // 添加高光效果
                            this.nextPieceCtx.fillStyle = 'rgba(255, 255, 255, 0.3)';
                            this.nextPieceCtx.fillRect(
                                offsetX + x * blockSize,
                                offsetY + y * blockSize,
                                blockSize,
                                3
                            );
                            this.nextPieceCtx.fillRect(
                                offsetX + x * blockSize,
                                offsetY + y * blockSize,
                                3,
                                blockSize
                            );
                        }
                    }
                }
            }
            
            update(time = 0) {
                if (this.gameOver || this.paused) return;
                
                const deltaTime = time - this.lastTime;
                this.lastTime = time;
                
                this.dropCounter += deltaTime;
                if (this.dropCounter > this.dropInterval) {
                    this.drop();
                }
                
                this.draw();
            }
        }
        
        // AI对手算法
        class TetrisAI {
            constructor(gameState, difficulty = 'medium') {
                this.gameState = gameState;
                this.difficulty = difficulty;
                this.thinkingTime = this.getThinkingTime();
                this.lastMoveTime = 0;
            }
            
            getThinkingTime() {
                switch (this.difficulty) {
                    case 'easy': return 300; // 300ms思考时间
