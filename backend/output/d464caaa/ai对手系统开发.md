# AI对手系统开发

**Agent**: coder

**Time**: 2026-02-19T15:28:56.410696

---

我将为你开发一个完整的俄罗斯方块对战游戏，包含基于启发式算法的AI对手系统。以下是完整的单文件HTML实现：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>俄罗斯方块对战 - AI对手</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            background-color: #111;
            color: #fff;
            font-family: 'Arial', sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        
        .game-container {
            display: flex;
            gap: 30px;
            align-items: flex-start;
        }
        
        .game-board {
            position: relative;
            border: 2px solid #444;
            background-color: #000;
        }
        
        .info-panel {
            background-color: #222;
            padding: 20px;
            border-radius: 10px;
            width: 200px;
        }
        
        .score {
            margin-bottom: 15px;
            font-size: 18px;
        }
        
        .controls {
            margin-top: 20px;
            font-size: 14px;
            line-height: 1.6;
        }
        
        .controls h3 {
            margin-top: 0;
            color: #4CAF50;
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
        
        .restart-btn {
            margin-top: 15px;
            padding: 10px 20px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        }
        
        .restart-btn:hover {
            background-color: #45a049;
        }
        
        .ai-status {
            margin-top: 15px;
            padding: 10px;
            background-color: #333;
            border-radius: 5px;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="game-container">
        <div class="game-board">
            <canvas id="playerCanvas" width="300" height="600"></canvas>
            <div class="game-over" id="playerGameOver">
                <h2>游戏结束</h2>
                <button class="restart-btn" onclick="restartGame()">重新开始</button>
            </div>
        </div>
        
        <div class="game-board">
            <canvas id="aiCanvas" width="300" height="600"></canvas>
            <div class="game-over" id="aiGameOver">
                <h2>AI游戏结束</h2>
                <button class="restart-btn" onclick="restartGame()">重新开始</button>
            </div>
        </div>
        
        <div class="info-panel">
            <div class="score">
                <div>玩家得分: <span id="playerScore">0</span></div>
                <div>AI得分: <span id="aiScore">0</span></div>
            </div>
            
            <div class="ai-status">
                <div>AI状态: <span id="aiStatus">思考中...</span></div>
                <div>决策深度: <span id="decisionDepth">0</span></div>
            </div>
            
            <div class="controls">
                <h3>操作说明</h3>
                <div>← → : 左右移动</div>
                <div>↑ : 旋转</div>
                <div>↓ : 加速下落</div>
                <div>空格 : 直接落下</div>
            </div>
        </div>
    </div>

    <script>
        // 游戏常量
        const COLS = 10;
        const ROWS = 20;
        const BLOCK_SIZE = 30;
        const INITIAL_SPEED = 1000; // 初始下落速度（毫秒）
        const SPEED_INCREMENT = 50; // 每消除一行后速度增加量
        const AI_THINK_INTERVAL = 100; // AI思考间隔（毫秒）
        
        // 方块形状定义
        const SHAPES = [
            // I形
            [
                [0, 0, 0, 0],
                [1, 1, 1, 1],
                [0, 0, 0, 0],
                [0, 0, 0, 0]
            ],
            // J形
            [
                [1, 0, 0],
                [1, 1, 1],
                [0, 0, 0]
            ],
            // L形
            [
                [0, 0, 1],
                [1, 1, 1],
                [0, 0, 0]
            ],
            // O形
            [
                [1, 1],
                [1, 1]
            ],
            // S形
            [
                [0, 1, 1],
                [1, 1, 0],
                [0, 0, 0]
            ],
            // T形
            [
                [0, 1, 0],
                [1, 1, 1],
                [0, 0, 0]
            ],
            // Z形
            [
                [1, 1, 0],
                [0, 1, 1],
                [0, 0, 0]
            ]
        ];
        
        // 方块颜色
        const COLORS = [
            '#FF0D72', '#0DC2FF', '#0DFF72', '#F538FF',
            '#FF8E0D', '#FFE138', '#3877FF'
        ];
        
        // 游戏状态
        let gameRunning = true;
        let playerScore = 0;
        let aiScore = 0;
        
        // 玩家游戏板
        const playerCanvas = document.getElementById('playerCanvas');
        const playerCtx = playerCanvas.getContext('2d');
        const playerBoard = Array(ROWS).fill().map(() => Array(COLS).fill(0));
        
        // AI游戏板
        const aiCanvas = document.getElementById('aiCanvas');
        const aiCtx = aiCanvas.getContext('2d');
        const aiBoard = Array(ROWS).fill().map(() => Array(COLS).fill(0));
        
        // 方块类
        class Tetromino {
            constructor(shape, color) {
                this.shape = shape;
                this.color = color;
                this.x = Math.floor(COLS / 2) - Math.floor(shape[0].length / 2);
                this.y = 0;
            }
            
            // 旋转方块
            rotate() {
                const N = this.shape.length;
                const rotated = Array(N).fill().map(() => Array(N).fill(0));
                
                for (let i = 0; i < N; i++) {
                    for (let j = 0; j < N; j++) {
                        rotated[j][N - 1 - i] = this.shape[i][j];
                    }
                }
                
                return rotated;
            }
            
            // 检查碰撞
            collides(board, dx = 0, dy = 0, newShape = null) {
                const shape = newShape || this.shape;
                
                for (let y = 0; y < shape.length; y++) {
                    for (let x = 0; x < shape[y].length; x++) {
                        if (shape[y][x] !== 0) {
                            const newX = this.x + x + dx;
                            const newY = this.y + y + dy;
                            
                            if (newX < 0 || newX >= COLS || newY >= ROWS) {
                                return true;
                            }
                            
                            if (newY >= 0 && board[newY][newX] !== 0) {
                                return true;
                            }
                        }
                    }
                }
                
                return false;
            }
            
            // 将方块固定到游戏板上
            lock(board) {
                for (let y = 0; y < this.shape.length; y++) {
                    for (let x = 0; x < this.shape[y].length; x++) {
                        if (this.shape[y][x] !== 0) {
                            const boardY = this.y + y;
                            const boardX = this.x + x;
                            
                            if (boardY >= 0) {
                                board[boardY][boardX] = this.color;
                            }
                        }
                    }
                }
            }
            
            // 移动方块
            move(board, dx, dy) {
                if (!this.collides(board, dx, dy)) {
                    this.x += dx;
                    this.y += dy;
                    return true;
                }
                return false;
            }
            
            // 旋转方块
            rotateIfPossible(board) {
                const rotated = this.rotate();
                if (!this.collides(board, 0, 0, rotated)) {
                    this.shape = rotated;
                    return true;
                }
                return false;
            }
            
            // 硬降落（直接落到最底部）
            hardDrop(board) {
                while (this.move(board, 0, 1)) {
                    // 继续下落直到碰撞
                }
            }
        }
        
        // 游戏类
        class TetrisGame {
            constructor(canvas, ctx, board, isAI = false) {
                this.canvas = canvas;
                this.ctx = ctx;
                this.board = board;
                this.isAI = isAI;
                this.currentPiece = null;
                this.nextPiece = null;
                this.score = 0;
                this.lines = 0;
                this.level = 1;
                this.dropInterval = INITIAL_SPEED;
                this.lastDropTime = 0;
                this.gameOver = false;
                this.aiThinkTimer = 0;
                
                this.init();
            }
            
            init() {
                this.spawnPiece();
                this.draw();
            }
            
            // 生成新方块
            spawnPiece() {
                if (this.nextPiece === null) {
                    const shapeIndex = Math.floor(Math.random() * SHAPES.length);
                    this.nextPiece = new Tetromino(
                        SHAPES[shapeIndex],
                        COLORS[shapeIndex]
                    );
                }
                
                this.currentPiece = this.nextPiece;
                this.nextPiece = null;
                
                // 生成下一个方块
                const shapeIndex = Math.floor(Math.random() * SHAPES.length);
                this.nextPiece = new Tetromino(
                    SHAPES[shapeIndex],
                    COLORS[shapeIndex]
                );
                
                // 检查游戏是否结束
                if (this.currentPiece.collides(this.board)) {
                    this.gameOver = true;
                    if (this.isAI) {
                        document.getElementById('aiGameOver').style.display = 'block';
                    } else {
                        document.getElementById('playerGameOver').style.display = 'block';
                    }
                    gameRunning = false;
                }
            }
            
            // 更新游戏状态
            update(currentTime) {
                if (this.gameOver) return;
                
                // AI思考逻辑
                if (this.isAI) {
                    this.aiThinkTimer += 16; // 假设每帧约16ms
                    if (this.aiThinkTimer >= AI_THINK_INTERVAL) {
                        this.aiMakeMove();
                        this.aiThinkTimer = 0;
                    }
                }
                
                // 方块下落
                if (currentTime - this.lastDropTime > this.dropInterval) {
                    if (!this.currentPiece.move(this.board, 0, 1)) {
                        this.lockPiece();
                        this.clearLines();
                        this.spawnPiece();
                    }
                    this.lastDropTime = currentTime;
                }
            }
            
            // 锁定方块
            lockPiece() {
                this.currentPiece.lock(this.board);
            }
            
            // 清除完整的行
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
                    this.score += linesCleared * 100 * this.level;
                    this.level = Math.floor(this.lines / 10) + 1;
                    this.dropInterval = Math.max(100, INITIAL_SPEED - (this.level - 1) * SPEED_INCREMENT);
                    
                    // 更新分数显示
                    if (this.isAI) {
                        aiScore = this.score;
                        document.getElementById('aiScore').textContent = aiScore;
                    } else {
                        playerScore = this.score;
                        document.getElementById('playerScore').textContent = playerScore;
                    }
                }
            }
            
            // 绘制游戏
            draw() {
                // 清空画布
                this.ctx.fillStyle = '#000';
                this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
                
                // 绘制网格
                this.drawGrid();
                
                // 绘制已锁定的方块
                for (let y = 0; y < ROWS; y++) {
                    for (let x = 0; x < COLS; x++) {
                        if (this.board[y][x] !== 0) {
                            this.drawBlock(x, y, this.board[y][x]);
                        }
                    }
                }
                
                // 绘制当前方块
                if (this.currentPiece) {
                    for (let y = 0; y < this.currentPiece.shape.length; y++) {
                        for (let x = 0; x < this.currentPiece.shape[y].length; x++) {
                            if (this.currentPiece.shape[y][x] !== 0) {
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
            
            // 绘制网格
            drawGrid() {
                this.ctx.strokeStyle = '#333';
                this.ctx.lineWidth = 0.5;
                
                // 绘制垂直线
                for (let x = 1; x < COLS; x++) {
                    this.ctx.beginPath();
                    this.ctx.moveTo(x * BLOCK_SIZE, 0);
                    this.ctx.lineTo(x * BLOCK_SIZE, this.canvas.height);
                    this.ctx.stroke();
                }
                
                // 绘制水平线
                for (let y = 1; y < ROWS; y++) {
                    this.ctx.beginPath();
                    this.ctx.moveTo(0, y * BLOCK_SIZE);
                    this.ctx.lineTo(this.canvas.width, y * BLOCK_SIZE);
                    this.ctx.stroke();
                }
            }
            
            // 绘制单个方块
            drawBlock(x, y, color) {
                this.ctx.fillStyle = color;
                this.ctx.fillRect(
                    x * BLOCK_SIZE,
                    y * BLOCK_SIZE,
                    BLOCK_SIZE - 1,
                    BLOCK_SIZE - 1
                );
                
                // 添加高光效果
                this.ctx.fillStyle = 'rgba(255, 255, 255, 0.3)';
                this.ctx.fillRect(
                    x * BLOCK_SIZE,
                    y * BLOCK_SIZE,
                    BLOCK_SIZE - 1,
                    4
                );
                this.ctx.fillRect(
                    x * BLOCK_SIZE,
                    y * BLOCK_SIZE,
                    4,
                    BLOCK_SIZE - 1
                );
            }
            
            // AI决策系统
            aiMakeMove() {
                if (!this.currentPiece || this.gameOver) return;
                
                // 更新AI状态显示
                document.getElementById('aiStatus').textContent = '计算中...';
                
                // 获取所有可能的移动
                const possibleMoves = this.getPossibleMoves();
                
                // 评估每种移动并选择最佳移动
                let bestMove = null;
                let bestScore = -Infinity;
                
                for (const move of possibleMoves) {
                    const score = this.evaluateMove(move);
                    if (score > bestScore) {
                        bestScore = score;
                        bestMove = move;
                    }
                }
                
                // 执行最佳移动
                if (bestMove) {
                    this.executeMove(bestMove);
                    document.getElementById('aiStatus').textContent = '移动完成';
                    document.getElementById('decisionDepth').textContent = bestMove.depth;
                }
            }
            
            // 获取所有可能的移动
            getPossibleMoves() {
                const moves = [];
                const originalPiece = {
                    shape: this.currentPiece.shape.map(row => [...row]),
                    x: this.currentPiece.x,
                    y: this.currentPiece.y
                };
                
                // 尝试所有可能的旋转
                const rotations = [0, 1, 2, 3]; // 0°, 90°, 180°, 270°
                
                for (const rotation of rotations) {
                    // 旋转方块
                    let rotatedShape = originalPiece.shape;
                    for (let i = 0; i < rotation; i++) {
                        const N = rotatedShape.length;
                        const newShape = Array(N).fill().map(() => Array(N).fill(0));
                        
                        for (let y = 0; y < N; y++) {
                            for (let x = 0; x < N; x++) {
                                newShape[x][N - 1 - y] = rotatedShape[y][x];
                            }
                        }
                        rotatedShape = newShape;
                    }
                    
                    // 尝试所有可能的水平位置
                    for (let x = 0; x < COLS; x++) {
                        // 计算需要移动的步数
                        const dx = x - originalPiece.x;
                        
                        // 模拟移动
                        const tempPiece = {
                            shape: rotatedShape,
                            x: originalPiece.x,
                            y: originalPiece.y
                        };
                        
                        // 检查是否可以移动到该位置
                        if (!this.checkCollision(tempPiece, dx, 0)) {
                            // 计算最终位置
                            const finalX = x;
                            const finalY = this.getDropPosition(rotatedShape, finalX);
                            
                            // 添加到可能的移动列表
                            moves.push({
                                rotation,
                                x: finalX,
                                y: finalY,
                                depth: rotation + 1
                            });
                        }
                    }
                }
                
                return moves;
            }
            
            // 检查碰撞
            checkCollision(piece, dx, dy) {
                for