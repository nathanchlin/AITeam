# 开发AI对手系统

**Agent**: coder

**Time**: 2026-02-19T16:30:56.831017

---

我将为您开发一个完整的俄罗斯方块对战游戏，包含AI对手系统。这个实现将包括评估函数、难度级别设置和游戏状态分析，确保AI具有挑战性但不会过于挫败玩家。

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>俄罗斯方块对战 - AI对手</title>
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
            gap: 20px;
            padding: 20px;
            background-color: #16213e;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.5);
        }
        
        .game-board {
            position: relative;
            border: 2px solid #0f3460;
            background-color: #0f3460;
        }
        
        canvas {
            display: block;
        }
        
        .info-panel {
            display: flex;
            flex-direction: column;
            gap: 20px;
            width: 200px;
        }
        
        .info-box {
            background-color: #0f3460;
            border-radius: 5px;
            padding: 15px;
            border: 1px solid #e94560;
        }
        
        .info-box h3 {
            margin-bottom: 10px;
            color: #e94560;
            font-size: 18px;
        }
        
        .score {
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .level {
            font-size: 16px;
            color: #f39c12;
        }
        
        .lines {
            font-size: 16px;
            color: #3498db;
        }
        
        .controls {
            background-color: #0f3460;
            border-radius: 5px;
            padding: 15px;
            border: 1px solid #e94560;
        }
        
        .controls h3 {
            margin-bottom: 10px;
            color: #e94560;
        }
        
        .control-item {
            margin: 5px 0;
            font-size: 14px;
        }
        
        .key {
            display: inline-block;
            background-color: #e94560;
            color: white;
            padding: 2px 6px;
            border-radius: 3px;
            margin-right: 5px;
            font-weight: bold;
        }
        
        .ai-difficulty {
            background-color: #0f3460;
            border-radius: 5px;
            padding: 15px;
            border: 1px solid #e94560;
        }
        
        .ai-difficulty h3 {
            margin-bottom: 10px;
            color: #e94560;
        }
        
        .difficulty-btn {
            display: block;
            width: 100%;
            padding: 8px;
            margin: 5px 0;
            background-color: #e94560;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            transition: background-color 0.3s;
        }
        
        .difficulty-btn:hover {
            background-color: #c13651;
        }
        
        .difficulty-btn.active {
            background-color: #3498db;
        }
        
        .game-over {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background-color: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            display: none;
        }
        
        .restart-btn {
            margin-top: 15px;
            padding: 10px 20px;
            background-color: #e94560;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        }
        
        .restart-btn:hover {
            background-color: #c13651;
        }
        
        .start-screen {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.9);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            z-index: 10;
        }
        
        .start-screen h1 {
            font-size: 36px;
            margin-bottom: 20px;
            color: #e94560;
        }
        
        .start-btn {
            padding: 15px 30px;
            background-color: #e94560;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 20px;
            transition: background-color 0.3s;
        }
        
        .start-btn:hover {
            background-color: #c13651;
        }
    </style>
</head>
<body>
    <div class="game-container">
        <div class="game-board">
            <canvas id="playerCanvas" width="300" height="600"></canvas>
            <div class="game-over" id="playerGameOver">
                <h2>游戏结束</h2>
                <p>最终得分: <span id="finalPlayerScore">0</span></p>
                <button class="restart-btn" onclick="restartGame()">重新开始</button>
            </div>
            <div class="start-screen" id="startScreen">
                <h1>俄罗斯方块对战</h1>
                <button class="start-btn" onclick="startGame()">开始游戏</button>
            </div>
        </div>
        
        <div class="info-panel">
            <div class="info-box">
                <h3>玩家信息</h3>
                <div class="score">得分: <span id="playerScore">0</span></div>
                <div class="level">等级: <span id="playerLevel">1</span></div>
                <div class="lines">消除行数: <span id="playerLines">0</span></div>
            </div>
            
            <div class="info-box">
                <h3>AI对手</h3>
                <div class="score">得分: <span id="aiScore">0</span></div>
                <div class="level">等级: <span id="aiLevel">1</span></div>
                <div class="lines">消除行数: <span id="aiLines">0</span></div>
            </div>
            
            <div class="ai-difficulty">
                <h3>AI难度</h3>
                <button class="difficulty-btn active" data-level="easy">简单</button>
                <button class="difficulty-btn" data-level="medium">中等</button>
                <button class="difficulty-btn" data-level="hard">困难</button>
                <button class="difficulty-btn" data-level="expert">专家</button>
            </div>
            
            <div class="controls">
                <h3>操作说明</h3>
                <div class="control-item"><span class="key">←</span> 左移</div>
                <div class="control-item"><span class="key">→</span> 右移</div>
                <div class="control-item"><span class="key">↓</span> 加速下落</div>
                <div class="control-item"><span class="key">↑</span> 旋转</div>
                <div class="control-item"><span class="key">空格</span> 直接落下</div>
            </div>
        </div>
        
        <div class="game-board">
            <canvas id="aiCanvas" width="300" height="600"></canvas>
            <div class="game-over" id="aiGameOver">
                <h2>AI游戏结束</h2>
                <p>最终得分: <span id="finalAiScore">0</span></p>
                <button class="restart-btn" onclick="restartGame()">重新开始</button>
            </div>
        </div>
    </div>

    <script>
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
            [[0, 0, 0, 0], [1, 1, 1, 1], [0, 0, 0, 0], [0, 0, 0, 0]], // I
            [[1, 0, 0], [1, 1, 1], [0, 0, 0]], // J
            [[0, 0, 1], [1, 1, 1], [0, 0, 0]], // L
            [[1, 1], [1, 1]], // O
            [[0, 1, 1], [1, 1, 0], [0, 0, 0]], // S
            [[0, 1, 0], [1, 1, 1], [0, 0, 0]], // T
            [[1, 1, 0], [0, 1, 1], [0, 0, 0]]  // Z
        ];
        
        // 游戏状态
        let gameRunning = false;
        let playerGame = null;
        let aiGame = null;
        let aiDifficulty = 'easy';
        
        // AI难度设置
        const DIFFICULTY_SETTINGS = {
            easy: {
                thinkTime: 500, // AI思考时间(毫秒)
                lookAhead: 1,   // 前瞻步数
                errorRate: 0.1  // 错误率
            },
            medium: {
                thinkTime: 300,
                lookAhead: 2,
                errorRate: 0.05
            },
            hard: {
                thinkTime: 150,
                lookAhead: 3,
                errorRate: 0.02
            },
            expert: {
                thinkTime: 50,
                lookAhead: 4,
                errorRate: 0.01
            }
        };
        
        // 方块类
        class Piece {
            constructor(shape, color) {
                this.shape = shape;
                this.color = color;
                this.x = Math.floor(COLS / 2) - Math.floor(shape[0].length / 2);
                this.y = 0;
            }
            
            rotate() {
                const rows = this.shape.length;
                const cols = this.shape[0].length;
                const rotated = Array(cols).fill().map(() => Array(rows).fill(0));
                
                for (let r = 0; r < rows; r++) {
                    for (let c = 0; c < cols; c++) {
                        rotated[c][rows - 1 - r] = this.shape[r][c];
                    }
                }
                
                return rotated;
            }
        }
        
        // 游戏类
        class TetrisGame {
            constructor(canvas, isAI = false) {
                this.canvas = canvas;
                this.ctx = canvas.getContext('2d');
                this.isAI = isAI;
                this.grid = Array(ROWS).fill().map(() => Array(COLS).fill(0));
                this.currentPiece = null;
                this.score = 0;
                this.level = 1;
                this.lines = 0;
                this.dropInterval = 1000;
                this.lastDrop = 0;
                this.gameOver = false;
                this.dropCounter = 0;
                this.lastTime = 0;
                
                // AI相关属性
                if (isAI) {
                    this.aiMoveQueue = null;
                    this.aiThinkTime = DIFFICULTY_SETTINGS[aiDifficulty].thinkTime;
                    this.aiLastThink = 0;
                }
            }
            
            // 生成新方块
            spawnPiece() {
                const shapeIndex = Math.floor(Math.random() * SHAPES.length);
                const shape = SHAPES[shapeIndex];
                const color = COLORS[shapeIndex];
                this.currentPiece = new Piece(shape, color);
                
                // 检查游戏是否结束
                if (this.collision()) {
                    this.gameOver = true;
                    return false;
                }
                return true;
            }
            
            // 碰撞检测
            collision() {
                const shape = this.currentPiece.shape;
                const offsetX = this.currentPiece.x;
                const offsetY = this.currentPiece.y;
                
                for (let r = 0; r < shape.length; r++) {
                    for (let c = 0; c < shape[r].length; c++) {
                        if (shape[r][c] !== 0) {
                            const newX = c + offsetX;
                            const newY = r + offsetY;
                            
                            if (newX < 0 || newX >= COLS || newY >= ROWS) {
                                return true;
                            }
                            
                            if (newY >= 0 && this.grid[newY][newX] !== 0) {
                                return true;
                            }
                        }
                    }
                }
                return false;
            }
            
            // 合并方块到网格
            merge() {
                const shape = this.currentPiece.shape;
                const offsetX = this.currentPiece.x;
                const offsetY = this.currentPiece.y;
                
                for (let r = 0; r < shape.length; r++) {
                    for (let c = 0; c < shape[r].length; c++) {
                        if (shape[r][c] !== 0) {
                            const newY = r + offsetY;
                            const newX = c + offsetX;
                            if (newY >= 0) {
                                this.grid[newY][newX] = this.currentPiece.color;
                            }
                        }
                    }
                }
            }
            
            // 清除完整的行
            clearLines() {
                let linesCleared = 0;
                
                for (let r = ROWS - 1; r >= 0; r--) {
                    if (this.grid[r].every(cell => cell !== 0)) {
                        this.grid.splice(r, 1);
                        this.grid.unshift(Array(COLS).fill(0));
                        linesCleared++;
                        r++; // 重新检查当前行
                    }
                }
                
                if (linesCleared > 0) {
                    this.lines += linesCleared;
                    this.score += linesCleared * 100 * this.level;
                    
                    // 每10行升一级
                    if (this.lines >= this.level * 10) {
                        this.level++;
                        this.dropInterval = Math.max(100, 1000 - (this.level - 1) * 100);
                    }
                    
                    // 更新UI
                    if (this.isAI) {
                        document.getElementById('aiScore').textContent = this.score;
                        document.getElementById('aiLevel').textContent = this.level;
                        document.getElementById('aiLines').textContent = this.lines;
                    } else {
                        document.getElementById('playerScore').textContent = this.score;
                        document.getElementById('playerLevel').textContent = this.level;
                        document.getElementById('playerLines').textContent = this.lines;
                    }
                }
                
                return linesCleared;
            }
            
            // 移动方块
            move(dir) {
                this.currentPiece.x += dir;
                if (this.collision()) {
                    this.currentPiece.x -= dir;
                    return false;
                }
                return true;
            }
            
            // 旋转方块
            rotate() {
                const originalShape = this.currentPiece.shape;
                this.currentPiece.shape = this.currentPiece.rotate();
                
                if (this.collision()) {
                    this.currentPiece.shape = originalShape;
                    return false;
                }
                return true;
            }
            
            // 硬降（直接落下）
            hardDrop() {
                let dropDistance = 0;
                while (!this.collision()) {
                    this.currentPiece.y++;
                    dropDistance++;
                }
                this.currentPiece.y--;
                this.score += dropDistance * 2;
                this.drop();
            }
            
            // 软降（加速下落）
            softDrop() {
                this.currentPiece.y++;
                if (this.collision()) {
                    this.currentPiece.y--;
                    this.drop();
                } else {
                    this.score += 1;
                }
            }
            
            // 固定方块
            drop() {
                this.merge();
                this.clearLines();
                if (!this.spawnPiece()) {
                    this.gameOver = true;
                }
            }
            
            // AI决策系统
            aiDecideMove() {
                if (!this.isAI || this.gameOver) return;
                
                const now = Date.now();
                if (now - this.aiLastThink < this.aiThinkTime) return;
                
                this.aiLastThink = now;
                
                // 获取可能的移动
                const possibleMoves = this.getAllPossibleMoves();
                
                // 评估每个移动
                let bestMove = null;
                let bestScore = -Infinity;
                
                for (const move of possibleMoves) {
                    const score = this.evaluateMove(move);
                    
                    // 添加随机性，使AI不完美
                    if (Math.random() < DIFFICULTY_SETTINGS[aiDifficulty].errorRate) {
                        // 随机选择一个不那么好的移动
                        if (score > bestScore * 0.7) {
                            bestMove = move;
                            bestScore = score;
                        }
                    } else {
                        // 选择最佳移动
                        if (score > bestScore) {
                            bestMove = move;
                            bestScore = score;
                        }
                    }
                }
                
                // 如果找到最佳移动，执行它
                if (bestMove) {
                    this.aiMoveQueue = bestMove;
                }
            }
            
            // 获取所有可能的移动
            getAllPossibleMoves() {
                const moves = [];
                const originalPiece = {
                    shape: this.currentPiece.shape,
                    x: this.currentPiece.x,
                   