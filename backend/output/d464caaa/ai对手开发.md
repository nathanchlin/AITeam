# AI对手开发

**Agent**: coder

**Time**: 2026-02-19T15:23:22.999248

---

我将为您创建一个完整的俄罗斯方块对战游戏，包含AI对手和难度调整系统。这个AI将具有智能决策能力，能够评估不同下落位置的价值，并根据游戏难度调整其表现。

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
            background-color: #121212;
            color: #ffffff;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        
        .game-container {
            display: flex;
            gap: 30px;
            flex-wrap: wrap;
            justify-content: center;
        }
        
        .game-board {
            position: relative;
            border: 2px solid #444;
            background-color: #1a1a1a;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.5);
        }
        
        canvas {
            display: block;
        }
        
        .info-panel {
            background-color: #1a1a1a;
            border: 2px solid #444;
            border-radius: 10px;
            padding: 20px;
            width: 200px;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.5);
        }
        
        .info-panel h3 {
            margin-top: 0;
            color: #4CAF50;
            text-align: center;
            border-bottom: 1px solid #444;
            padding-bottom: 10px;
        }
        
        .info-panel p {
            margin: 10px 0;
            font-size: 14px;
        }
        
        .score {
            font-size: 18px;
            font-weight: bold;
            color: #FFC107;
        }
        
        .level {
            font-size: 16px;
            color: #2196F3;
        }
        
        .controls {
            margin-top: 20px;
            text-align: center;
        }
        
        button {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 4px 2px;
            cursor: pointer;
            border-radius: 5px;
            transition: background-color 0.3s;
        }
        
        button:hover {
            background-color: #45a049;
        }
        
        .difficulty-selector {
            margin-top: 15px;
        }
        
        select {
            width: 100%;
            padding: 8px;
            margin-top: 5px;
            background-color: #333;
            color: white;
            border: 1px solid #555;
            border-radius: 4px;
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
        
        .next-piece {
            margin-top: 15px;
        }
        
        .next-piece canvas {
            border: 1px solid #444;
            margin-top: 5px;
        }
    </style>
</head>
<body>
    <div class="game-container">
        <div>
            <h2 style="text-align: center;">玩家</h2>
            <div class="game-board">
                <canvas id="playerCanvas" width="300" height="600"></canvas>
                <div class="game-over" id="playerGameOver">
                    <h3>游戏结束</h3>
                    <p>最终得分: <span id="playerFinalScore">0</span></p>
                    <button onclick="resetGame()">重新开始</button>
                </div>
            </div>
            <div class="controls">
                <div>
                    <p>← → : 左右移动</p>
                    <p>↑ : 旋转</p>
                    <p>↓ : 加速下落</p>
                    <p>空格 : 直接落下</p>
                </div>
                <button onclick="togglePause()">暂停/继续</button>
            </div>
        </div>
        
        <div>
            <h2 style="text-align: center;">AI对手</h2>
            <div class="game-board">
                <canvas id="aiCanvas" width="300" height="600"></canvas>
                <div class="game-over" id="aiGameOver">
                    <h3>AI游戏结束</h3>
                    <p>最终得分: <span id="aiFinalScore">0</span></p>
                </div>
            </div>
        </div>
        
        <div class="info-panel">
            <h3>游戏信息</h3>
            <div class="player-info">
                <p>得分: <span class="score" id="playerScore">0</span></p>
                <p>等级: <span class="level" id="playerLevel">1</span></p>
                <p>消除行数: <span id="playerLines">0</span></p>
            </div>
            
            <div class="next-piece">
                <h4>下一个方块:</h4>
                <canvas id="nextPieceCanvas" width="100" height="100"></canvas>
            </div>
            
            <div class="difficulty-selector">
                <h4>AI难度:</h4>
                <select id="difficultySelect">
                    <option value="easy">简单</option>
                    <option value="medium" selected>中等</option>
                    <option value="hard">困难</option>
                    <option value="expert">专家</option>
                </select>
            </div>
            
            <div class="ai-info">
                <p>AI得分: <span class="score" id="aiScore">0</span></p>
                <p>AI等级: <span class="level" id="aiLevel">1</span></p>
                <p>AI消除行数: <span id="aiLines">0</span></p>
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
            [[1, 1, 1, 1]], // I
            [[1, 1], [1, 1]], // O
            [[1, 1, 1], [0, 1, 0]], // T
            [[1, 1, 1], [1, 0, 0]], // L
            [[1, 1, 1], [0, 0, 1]], // J
            [[0, 1, 1], [1, 1, 0]], // S
            [[1, 1, 0], [0, 1, 1]]  // Z
        ];
        
        // 方块颜色
        const COLORS = [
            '#00FFFF', // I - 青色
            '#FFFF00', // O - 黄色
            '#800080', // T - 紫色
            '#FFA500', // L - 橙色
            '#0000FF', // J - 蓝色
            '#00FF00', // S - 绿色
            '#FF0000'  // Z - 红色
        ];
        
        // 游戏状态
        let playerGame = null;
        let aiGame = null;
        let gamePaused = false;
        let gameRunning = true;
        
        // 方块类
        class Piece {
            constructor(shape, color) {
                this.shape = shape;
                this.color = color;
                this.x = Math.floor(COLS / 2) - Math.floor(shape[0].length / 2);
                this.y = 0;
            }
            
            rotate() {
                const rotated = [];
                const rows = this.shape.length;
                const cols = this.shape[0].length;
                
                for (let i = 0; i < cols; i++) {
                    rotated[i] = [];
                    for (let j = rows - 1; j >= 0; j--) {
                        rotated[i].push(this.shape[j][i]);
                    }
                }
                
                return rotated;
            }
        }
        
        // 游戏板类
        class Board {
            constructor(canvas, isAI = false) {
                this.canvas = canvas;
                this.ctx = canvas.getContext('2d');
                this.isAI = isAI;
                this.grid = Array(ROWS).fill().map(() => Array(COLS).fill(0));
                this.currentPiece = null;
                this.nextPiece = null;
                this.score = 0;
                this.level = 1;
                this.lines = 0;
                this.dropCounter = 0;
                this.dropInterval = 1000; // 初始下落间隔（毫秒）
                this.lastTime = 0;
                this.gameOver = false;
                this.aiDifficulty = 'medium';
                
                // AI相关属性
                if (isAI) {
                    this.aiThinkingTime = 500; // AI思考时间
                    this.aiDecisionTime = 0;
                    this.aiBestMove = null;
                }
            }
            
            reset() {
                this.grid = Array(ROWS).fill().map(() => Array(COLS).fill(0));
                this.score = 0;
                this.level = 1;
                this.lines = 0;
                this.dropInterval = 1000;
                this.gameOver = false;
                this.currentPiece = this.getRandomPiece();
                this.nextPiece = this.getRandomPiece();
                
                if (this.isAI) {
                    this.aiDecisionTime = 0;
                    this.aiBestMove = null;
                }
            }
            
            getRandomPiece() {
                const shapeIndex = Math.floor(Math.random() * SHAPES.length);
                return new Piece(SHAPES[shapeIndex], COLORS[shapeIndex]);
            }
            
            isValidMove(piece, dx = 0, dy = 0, newShape = null) {
                const shape = newShape || piece.shape;
                const newX = piece.x + dx;
                const newY = piece.y + dy;
                
                for (let y = 0; y < shape.length; y++) {
                    for (let x = 0; x < shape[y].length; x++) {
                        if (shape[y][x] !== 0) {
                            const boardX = newX + x;
                            const boardY = newY + y;
                            
                            if (boardX < 0 || boardX >= COLS || boardY >= ROWS) {
                                return false;
                            }
                            
                            if (boardY >= 0 && this.grid[boardY][boardX] !== 0) {
                                return false;
                            }
                        }
                    }
                }
                
                return true;
            }
            
            lockPiece() {
                for (let y = 0; y < this.currentPiece.shape.length; y++) {
                    for (let x = 0; x < this.currentPiece.shape[y].length; x++) {
                        if (this.currentPiece.shape[y][x] !== 0) {
                            const boardX = this.currentPiece.x + x;
                            const boardY = this.currentPiece.y + y;
                            
                            if (boardY >= 0) {
                                this.grid[boardY][boardX] = this.currentPiece.color;
                            }
                        }
                    }
                }
                
                this.clearLines();
                this.currentPiece = this.nextPiece;
                this.nextPiece = this.getRandomPiece();
                
                // 检查游戏是否结束
                if (!this.isValidMove(this.currentPiece)) {
                    this.gameOver = true;
                    if (!this.isAI) {
                        document.getElementById('playerGameOver').style.display = 'block';
                        document.getElementById('playerFinalScore').textContent = this.score;
                    } else {
                        document.getElementById('aiGameOver').style.display = 'block';
                        document.getElementById('aiFinalScore').textContent = this.score;
                    }
                    gameRunning = false;
                }
            }
            
            clearLines() {
                let linesCleared = 0;
                
                for (let y = ROWS - 1; y >= 0; y--) {
                    if (this.grid[y].every(cell => cell !== 0)) {
                        this.grid.splice(y, 1);
                        this.grid.unshift(Array(COLS).fill(0));
                        linesCleared++;
                        y++; // 重新检查当前行
                    }
                }
                
                if (linesCleared > 0) {
                    this.lines += linesCleared;
                    this.score += linesCleared * 100 * this.level;
                    
                    // 每清除10行提升一级
                    if (this.lines >= this.level * 10) {
                        this.level++;
                        this.dropInterval = Math.max(100, 1000 - (this.level - 1) * 100);
                    }
                }
            }
            
            drop() {
                if (this.isValidMove(this.currentPiece, 0, 1)) {
                    this.currentPiece.y++;
                } else {
                    this.lockPiece();
                }
            }
            
            hardDrop() {
                while (this.isValidMove(this.currentPiece, 0, 1)) {
                    this.currentPiece.y++;
                    this.score += 2;
                }
                this.lockPiece();
            }
            
            moveLeft() {
                if (this.isValidMove(this.currentPiece, -1, 0)) {
                    this.currentPiece.x--;
                }
            }
            
            moveRight() {
                if (this.isValidMove(this.currentPiece, 1, 0)) {
                    this.currentPiece.x++;
                }
            }
            
            rotatePiece() {
                const rotated = this.currentPiece.rotate();
                if (this.isValidMove(this.currentPiece, 0, 0, rotated)) {
                    this.currentPiece.shape = rotated;
                }
            }
            
            // AI相关方法
            setDifficulty(difficulty) {
                this.aiDifficulty = difficulty;
                switch (difficulty) {
                    case 'easy':
                        this.aiThinkingTime = 800;
                        break;
                    case 'medium':
                        this.aiThinkingTime = 500;
                        break;
                    case 'hard':
                        this.aiThinkingTime = 300;
                        break;
                    case 'expert':
                        this.aiThinkingTime = 100;
                        break;
                }
            }
            
            // 评估函数 - 计算某个位置的分数
            evaluatePosition(piece, x, y, shape) {
                // 创建临时游戏板
                const tempGrid = this.grid.map(row => [...row]);
                
                // 将方块放置在临时游戏板上
                for (let py = 0; py < shape.length; py++) {
                    for (let px = 0; px < shape[py].length; px++) {
                        if (shape[py][px] !== 0) {
                            const boardX = x + px;
                            const boardY = y + py;
                            if (boardY >= 0 && boardY < ROWS && boardX >= 0 && boardX < COLS) {
                                tempGrid[boardY][boardX] = 1; // 标记为已占用
                            }
                        }
                    }
                }
                
                let score = 0;
                let holes = 0;
                let bumpiness = 0;
                let maxHeight = 0;
                
                // 计算列高度
                const colHeights = Array(COLS).fill(0);
                for (let x = 0; x < COLS; x++) {
                    for (let y = ROWS - 1; y >= 0; y--) {
                        if (tempGrid[y][x] !== 0) {
                            colHeights[x] = ROWS - y;
                            maxHeight = Math.max(maxHeight, colHeights[x]);
                            break;
                        }
                    }
                }
                
                // 计算孔洞数量
                for (let x = 0; x < COLS; x++) {
                    let blockFound = false;
                    for (let y = ROWS - 1; y >= 0; y--) {
                        if (tempGrid[y][x] !== 0) {
                            blockFound = true;
                        } else if (blockFound) {
                            holes++;
                        }
                    }
                }
                
                // 计算表面不平整度
                for (let x = 1; x < COLS; x++) {
                    bumpiness += Math.abs(colHeights[x] - colHeights[x - 1]);
                }
                
                // 计算可能消除的行数
                let lines = 0;
                for (let y = 0; y < ROWS; y++) {
                    if (tempGrid[y].every(cell => cell !== 0)) {
                        lines++;
                    }
                }
                
                // 评分计算
                score += lines * 1000; // 消除行数得分最高
                score -= holes * 10; // 孔洞扣分
                score -= maxHeight * 0.5; // 高度扣分
                score -= bumpiness * 0.2; // 不平整度扣分
                
                // 根据难度添加随机性
                if (this.aiDifficulty === 'easy') {
                    score += Math.random() * 200 - 100; // 添加较大随机性
                } else if (this.aiDifficulty === 'medium') {
                    score += Math.random() * 100 - 50; // 添加中等随机性
                }
                
                return score;
            }
            
            // AI决策 - 找到最佳移动
            findBestMove() {
                const possibleMoves = [];
                
                // 尝试所有可能的x位置和旋转
                for (let rotation = 0; rotation < 4; rotation++) {
                    let shape = this.currentPiece.shape;
                    
                    // 应用旋转
                    for (let r = 0; r < rotation; r++) {
                        const rotated = [];
                        const rows = shape.length;
                        const cols = shape[0].length;
                        
                        for (let i = 0; i < cols; i++) {
                            rotated[i] = [];
                            for (let j = rows - 1; j >= 0; j--) {
                                rotated[i].push(shape[j][i]);
                            }
                        }
                        shape = rotated;
                    }
                    
                    // 尝试所有可能的x位置
                    for (let x = 