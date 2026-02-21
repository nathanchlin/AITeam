# AI对手算法开发

**Agent**: coder

**Time**: 2026-02-19T15:15:34.818609

---

我将为您创建一个完整的俄罗斯方块对战游戏，包含AI对手的决策算法。这个实现将包括评估函数、策略选择和难度级别设置。

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
            padding: 20px;
            font-family: 'Arial', sans-serif;
            background-color: #1a1a2e;
            color: #eee;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        
        h1 {
            text-align: center;
            color: #f39c12;
            margin-bottom: 20px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }
        
        .game-container {
            display: flex;
            gap: 30px;
            margin-bottom: 20px;
        }
        
        .game-board {
            position: relative;
        }
        
        canvas {
            border: 2px solid #34495e;
            background-color: #2c3e50;
            box-shadow: 0 0 10px rgba(0,0,0,0.5);
        }
        
        .game-info {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        
        .info-panel {
            background-color: #34495e;
            border-radius: 8px;
            padding: 15px;
            min-width: 200px;
            box-shadow: 0 0 5px rgba(0,0,0,0.3);
        }
        
        .info-panel h3 {
            margin-top: 0;
            color: #f39c12;
            border-bottom: 1px solid #555;
            padding-bottom: 8px;
        }
        
        .score {
            font-size: 24px;
            font-weight: bold;
            color: #2ecc71;
            margin: 10px 0;
        }
        
        .controls {
            margin-top: 20px;
            text-align: center;
        }
        
        .controls button {
            background-color: #3498db;
            color: white;
            border: none;
            padding: 10px 20px;
            margin: 0 5px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            transition: background-color 0.3s;
        }
        
        .controls button:hover {
            background-color: #2980b9;
        }
        
        .controls button:active {
            transform: translateY(1px);
        }
        
        .difficulty-selector {
            margin-top: 10px;
        }
        
        .difficulty-selector select {
            background-color: #34495e;
            color: white;
            border: 1px solid #555;
            padding: 8px;
            border-radius: 4px;
            font-size: 16px;
            width: 100%;
        }
        
        .next-piece {
            display: grid;
            grid-template-columns: repeat(4, 20px);
            grid-template-rows: repeat(4, 20px);
            gap: 1px;
            margin: 10px auto;
            width: fit-content;
        }
        
        .next-cell {
            width: 20px;
            height: 20px;
            border: 1px solid #555;
        }
        
        .game-over {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background-color: rgba(0, 0, 0, 0.8);
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            display: none;
        }
        
        .game-over h2 {
            color: #e74c3c;
            margin-top: 0;
        }
        
        .pause-overlay {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.7);
            display: none;
            justify-content: center;
            align-items: center;
            font-size: 36px;
            color: white;
        }
    </style>
</head>
<body>
    <h1>俄罗斯方块对战 - AI对手</h1>
    
    <div class="game-container">
        <div class="game-board">
            <canvas id="playerCanvas" width="300" height="600"></canvas>
            <div class="game-over" id="playerGameOver">
                <h2>游戏结束</h2>
                <p>最终得分: <span id="playerFinalScore">0</span></p>
            </div>
            <div class="pause-overlay" id="playerPause">暂停</div>
        </div>
        
        <div class="game-info">
            <div class="info-panel">
                <h3>玩家信息</h3>
                <div class="score">得分: <span id="playerScore">0</span></div>
                <div class="score">消除行数: <span id="playerLines">0</span></div>
                <div class="score">等级: <span id="playerLevel">1</span></div>
                <h4 style="margin-top: 15px;">下一个方块:</h4>
                <div class="next-piece" id="playerNextPiece"></div>
            </div>
            
            <div class="info-panel">
                <h3>AI对手信息</h3>
                <div class="score">得分: <span id="aiScore">0</span></div>
                <div class="score">消除行数: <span id="aiLines">0</span></div>
                <div class="score">等级: <span id="aiLevel">1</span></div>
                <h4 style="margin-top: 15px;">下一个方块:</h4>
                <div class="next-piece" id="aiNextPiece"></div>
            </div>
            
            <div class="info-panel">
                <h3>游戏控制</h3>
                <div class="difficulty-selector">
                    <label for="difficulty">AI难度:</label>
                    <select id="difficulty">
                        <option value="easy">简单</option>
                        <option value="medium" selected>中等</option>
                        <option value="hard">困难</option>
                        <option value="expert">专家</option>
                    </select>
                </div>
                <div class="controls">
                    <button id="startBtn">开始游戏</button>
                    <button id="pauseBtn">暂停</button>
                    <button id="resetBtn">重置</button>
                </div>
                <div style="margin-top: 15px; font-size: 14px;">
                    <p><strong>操作说明:</strong></p>
                    <p>← → : 左右移动</p>
                    <p>↓ : 加速下落</p>
                    <p>↑ : 旋转</p>
                    <p>空格 : 直接落下</p>
                </div>
            </div>
        </div>
        
        <div class="game-board">
            <canvas id="aiCanvas" width="300" height="600"></canvas>
            <div class="game-over" id="aiGameOver">
                <h2>AI游戏结束</h2>
                <p>最终得分: <span id="aiFinalScore">0</span></p>
            </div>
            <div class="pause-overlay" id="aiPause">暂停</div>
        </div>
    </div>

    <script>
        // 游戏常量
        const COLS = 10;
        const ROWS = 20;
        const BLOCK_SIZE = 30;
        
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
            '#00f0f0', // I - 青色
            '#0000f0', // J - 蓝色
            '#f0a000', // L - 橙色
            '#f0f000', // O - 黄色
            '#00f000', // S - 绿色
            '#a000f0', // T - 紫色
            '#f00000'  // Z - 红色
        ];
        
        // 游戏状态
        class GameState {
            constructor(canvas, isAI = false) {
                this.canvas = canvas;
                this.ctx = canvas.getContext('2d');
                this.isAI = isAI;
                this.board = Array(ROWS).fill().map(() => Array(COLS).fill(0));
                this.currentPiece = null;
                this.nextPiece = null;
                this.score = 0;
                this.lines = 0;
                this.level = 1;
                this.gameOver = false;
                this.paused = false;
                this.dropInterval = 1000; // 初始下落间隔(毫秒)
                this.lastDropTime = 0;
                this.aiDifficulty = 'medium';
                
                // AI相关属性
                this.aiThinking = false;
                this.aiMoveDelay = 0;
                this.aiBestMove = null;
                
                // 生成第一个方块
                this.spawnPiece();
            }
            
            // 生成新方块
            spawnPiece() {
                if (this.nextPiece === null) {
                    this.nextPiece = {
                        shape: Math.floor(Math.random() * SHAPES.length),
                        rotation: 0,
                        x: Math.floor(COLS / 2) - Math.floor(SHAPES[0][0].length / 2),
                        y: 0
                    };
                }
                
                this.currentPiece = this.nextPiece;
                this.nextPiece = {
                    shape: Math.floor(Math.random() * SHAPES.length),
                    rotation: 0,
                    x: Math.floor(COLS / 2) - Math.floor(SHAPES[0][0].length / 2),
                    y: 0
                };
                
                // 检查游戏是否结束
                if (this.checkCollision(this.currentPiece)) {
                    this.gameOver = true;
                }
            }
            
            // 检查碰撞
            checkCollision(piece, offsetX = 0, offsetY = 0, rotation = null) {
                const shape = rotation !== null ? this.getRotatedShape(piece.shape, rotation) : SHAPES[piece.shape];
                
                for (let y = 0; y < shape.length; y++) {
                    for (let x = 0; x < shape[y].length; x++) {
                        if (shape[y][x] !== 0) {
                            const boardX = piece.x + x + offsetX;
                            const boardY = piece.y + y + offsetY;
                            
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
            
            // 获取旋转后的形状
            getRotatedShape(shapeIndex, rotation) {
                let shape = SHAPES[shapeIndex];
                for (let i = 0; i < rotation; i++) {
                    const rows = shape.length;
                    const cols = shape[0].length;
                    const newShape = Array(cols).fill().map(() => Array(rows).fill(0));
                    
                    for (let y = 0; y < rows; y++) {
                        for (let x = 0; x < cols; x++) {
                            newShape[x][rows - 1 - y] = shape[y][x];
                        }
                    }
                    
                    shape = newShape;
                }
                return shape;
            }
            
            // 移动方块
            movePiece(dx, dy) {
                if (!this.currentPiece || this.gameOver || this.paused) return false;
                
                if (!this.checkCollision(this.currentPiece, dx, dy)) {
                    this.currentPiece.x += dx;
                    this.currentPiece.y += dy;
                    return true;
                }
                return false;
            }
            
            // 旋转方块
            rotatePiece() {
                if (!this.currentPiece || this.gameOver || this.paused) return false;
                
                const newRotation = (this.currentPiece.rotation + 1) % 4;
                if (!this.checkCollision(this.currentPiece, 0, 0, newRotation)) {
                    this.currentPiece.rotation = newRotation;
                    return true;
                }
                
                // 尝试墙踢
                for (let kick of [-1, 1, -2, 2]) {
                    if (!this.checkCollision(this.currentPiece, kick, 0, newRotation)) {
                        this.currentPiece.x += kick;
                        this.currentPiece.rotation = newRotation;
                        return true;
                    }
                }
                
                return false;
            }
            
            // 直接落下
            hardDrop() {
                if (!this.currentPiece || this.gameOver || this.paused) return;
                
                let dropDistance = 0;
                while (!this.checkCollision(this.currentPiece, 0, dropDistance + 1)) {
                    dropDistance++;
                }
                
                this.currentPiece.y += dropDistance;
                this.lockPiece();
            }
            
            // 锁定方块
            lockPiece() {
                const shape = SHAPES[this.currentPiece.shape];
                
                for (let y = 0; y < shape.length; y++) {
                    for (let x = 0; x < shape[y].length; x++) {
                        if (shape[y][x] !== 0) {
                            const boardY = this.currentPiece.y + y;
                            const boardX = this.currentPiece.x + x;
                            
                            if (boardY >= 0) {
                                this.board[boardY][boardX] = this.currentPiece.shape + 1;
                            }
                        }
                    }
                }
                
                // 检查并清除完整的行
                this.clearLines();
                
                // 生成新方块
                this.spawnPiece();
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
                    // 计算得分
                    const points = [0, 100, 300, 500, 800];
                    this.score += points[linesCleared] * this.level;
                    this.lines += linesCleared;
                    
                    // 更新等级
                    this.level = Math.floor(this.lines / 10) + 1;
                    this.dropInterval = Math.max(100, 1000 - (this.level - 1) * 100);
                }
            }
            
            // 更新游戏状态
            update(timestamp) {
                if (this.gameOver || this.paused) return;
                
                // 处理AI决策
                if (this.isAI && !this.aiThinking && this.currentPiece) {
                    this.calculateBestMove();
                    this.aiThinking = true;
                }
                
                // 执行AI移动
                if (this.isAI && this.aiThinking && this.aiBestMove && this.aiMoveDelay <= 0) {
                    this.executeAIMove();
                    this.aiThinking = false;
                    this.aiMoveDelay = 200; // AI移动之间的延迟
                }
                
                if (this.aiMoveDelay > 0) {
                    this.aiMoveDelay -= 16; // 假设60FPS，每帧约16ms
                }
                
                // 自动下落
                if (timestamp - this.lastDropTime > this.dropInterval) {
                    if (!this.movePiece(0, 1)) {
                        this.lockPiece();
                    }
                    this.lastDropTime = timestamp;
                }
            }
            
            // 计算AI最佳移动
            calculateBestMove() {
                const possibleMoves = [];
                const piece = this.currentPiece;
                
                // 尝试所有可能的旋转和位置
                for (let rotation = 0; rotation < 4; rotation++) {
                    const rotatedShape = this.getRotatedShape(piece.shape, rotation);
                    
                    // 找到该旋转下的最左和最右位置
                    let minX = COLS, maxX = -1;
                    for (let y = 0; y < rotatedShape.length; y++) {
                        for (let x = 0; x < rotatedShape[y].length; x++) {
                            if (rotatedShape[y][x] !== 0) {
                                minX = Math.min(minX, x);
                                maxX = Math.max(maxX, x);
                            }
                        }
                    }
                    
                    // 尝试所有可能的x位置
                    for (let x = -minX; x <= COLS - maxX; x++) {
                        // 找到可以放置的最低位置
                        let y = 0;
                        while (!this.checkCollision({ shape: piece.shape, rotation, x, y }, 0, 1)) {
                            y++;
                        }
                        
                        // 创建一个