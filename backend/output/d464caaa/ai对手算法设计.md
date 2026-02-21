# AI对手算法设计

**Agent**: coder

**Time**: 2026-02-19T15:12:32.910152

---

我将为你创建一个完整的俄罗斯方块对战游戏，包含一个智能的AI对手。这个AI将使用启发式算法来做出决策，确保游戏难度合理且具有挑战性。

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>俄罗斯方块对战</title>
    <style>
        body {
            margin: 0;
            padding: 20px;
            background-color: #222;
            color: #fff;
            font-family: 'Arial', sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        
        h1 {
            margin-bottom: 20px;
            color: #4CAF50;
            text-shadow: 0 0 10px rgba(76, 175, 80, 0.5);
        }
        
        .game-container {
            display: flex;
            gap: 30px;
            align-items: flex-start;
        }
        
        .game-board {
            position: relative;
            background-color: #111;
            border: 2px solid #444;
            box-shadow: 0 0 15px rgba(0, 0, 0, 0.5);
        }
        
        canvas {
            display: block;
            background-color: #000;
        }
        
        .game-info {
            display: flex;
            flex-direction: column;
            gap: 20px;
            min-width: 200px;
        }
        
        .info-box {
            background-color: #333;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.3);
        }
        
        .info-box h3 {
            margin-top: 0;
            color: #4CAF50;
            border-bottom: 1px solid #555;
            padding-bottom: 5px;
        }
        
        .score {
            font-size: 24px;
            font-weight: bold;
            color: #FFC107;
            text-shadow: 0 0 5px rgba(255, 193, 7, 0.5);
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
            margin: 5px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            transition: background-color 0.3s;
        }
        
        button:hover {
            background-color: #45a049;
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
        
        .next-piece {
            display: grid;
            grid-template-columns: repeat(4, 20px);
            grid-template-rows: repeat(4, 20px);
            gap: 1px;
            margin-top: 10px;
            background-color: #222;
            padding: 5px;
            border-radius: 4px;
        }
        
        .next-piece-cell {
            background-color: #111;
            border-radius: 2px;
        }
    </style>
</head>
<body>
    <h1>俄罗斯方块对战</h1>
    
    <div class="game-container">
        <div class="game-board">
            <canvas id="playerCanvas" width="300" height="600"></canvas>
            <div class="game-over" id="playerGameOver">
                <h2>游戏结束</h2>
                <p>最终得分: <span id="finalScore">0</span></p>
                <button onclick="game.restart()">重新开始</button>
            </div>
        </div>
        
        <div class="game-info">
            <div class="info-box">
                <h3>玩家</h3>
                <p>得分: <span class="score" id="playerScore">0</span></p>
                <p>消除行数: <span id="playerLines">0</span></p>
                <p>等级: <span id="playerLevel">1</span></p>
            </div>
            
            <div class="info-box">
                <h3>下一个方块</h3>
                <div class="next-piece" id="nextPiece"></div>
            </div>
            
            <div class="info-box">
                <h3>操作说明</h3>
                <p>← → : 左右移动</p>
                <p>↑ : 旋转</p>
                <p>↓ : 加速下落</p>
                <p>空格 : 直接落下</p>
            </div>
            
            <div class="controls">
                <button onclick="game.togglePause()">暂停/继续</button>
                <button onclick="game.restart()">重新开始</button>
            </div>
        </div>
        
        <div class="game-board">
            <canvas id="aiCanvas" width="300" height="600"></canvas>
            <div class="game-over" id="aiGameOver">
                <h2>AI游戏结束</h2>
                <p>最终得分: <span id="aiFinalScore">0</span></p>
            </div>
        </div>
        
        <div class="game-info">
            <div class="info-box">
                <h3>AI对手</h3>
                <p>得分: <span class="score" id="aiScore">0</span></p>
                <p>消除行数: <span id="aiLines">0</span></p>
                <p>等级: <span id="aiLevel">1</span></p>
            </div>
            
            <div class="info-box">
                <h3>AI状态</h3>
                <p id="aiStatus">思考中...</p>
                <p id="aiThinkingTime">决策时间: 0ms</p>
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
            [[1, 1, 1, 1]], // I
            [[1, 1], [1, 1]], // O
            [[0, 1, 0], [1, 1, 1]], // T
            [[1, 1, 0], [0, 1, 1]], // S
            [[0, 1, 1], [1, 1, 0]], // Z
            [[1, 0, 0], [1, 1, 1]], // J
            [[0, 0, 1], [1, 1, 1]]  // L
        ];
        
        // 游戏类
        class TetrisGame {
            constructor(canvasId, isAI = false) {
                this.canvas = document.getElementById(canvasId);
                this.ctx = this.canvas.getContext('2d');
                this.isAI = isAI;
                this.board = this.createBoard();
                this.currentPiece = null;
                this.nextPiece = null;
                this.score = 0;
                this.lines = 0;
                this.level = 1;
                this.gameOver = false;
                this.paused = false;
                this.dropCounter = 0;
                this.lastTime = 0;
                this.dropInterval = 1000; // 初始下落间隔（毫秒）
                
                // AI相关属性
                this.aiStatus = document.getElementById(isAI ? 'aiStatus' : null);
                this.aiThinkingTime = document.getElementById(isAI ? 'aiThinkingTime' : null);
                
                // 初始化游戏
                this.init();
            }
            
            createBoard() {
                return Array(ROWS).fill().map(() => Array(COLS).fill(0));
            }
            
            init() {
                // 生成第一个方块
                this.spawnPiece();
                
                // 如果是AI，开始自动游戏
                if (this.isAI) {
                    this.startAI();
                }
            }
            
            // 生成新方块
            spawnPiece() {
                if (!this.nextPiece) {
                    this.nextPiece = this.createRandomPiece();
                }
                
                this.currentPiece = this.nextPiece;
                this.nextPiece = this.createRandomPiece();
                
                // 更新下一个方块的显示
                if (!this.isAI) {
                    this.updateNextPieceDisplay();
                }
                
                // 检查游戏是否结束
                if (this.collision()) {
                    this.gameOver = true;
                    if (!this.isAI) {
                        document.getElementById('playerGameOver').style.display = 'block';
                        document.getElementById('finalScore').textContent = this.score;
                    } else {
                        document.getElementById('aiGameOver').style.display = 'block';
                        document.getElementById('aiFinalScore').textContent = this.score;
                    }
                }
            }
            
            // 创建随机方块
            createRandomPiece() {
                const typeId = Math.floor(Math.random() * SHAPES.length);
                return {
                    shape: SHAPES[typeId],
                    color: COLORS[typeId],
                    x: Math.floor(COLS / 2) - Math.floor(SHAPES[typeId][0].length / 2),
                    y: 0,
                    rotation: 0
                };
            }
            
            // 碰撞检测
            collision() {
                for (let y = 0; y < this.currentPiece.shape.length; y++) {
                    for (let x = 0; x < this.currentPiece.shape[y].length; x++) {
                        if (this.currentPiece.shape[y][x]) {
                            const boardX = this.currentPiece.x + x;
                            const boardY = this.currentPiece.y + y;
                            
                            if (
                                boardX < 0 || 
                                boardX >= COLS || 
                                boardY >= ROWS ||
                                (boardY >= 0 && this.board[boardY][boardX])
                            ) {
                                return true;
                            }
                        }
                    }
                }
                return false;
            }
            
            // 合并方块到游戏板
            merge() {
                for (let y = 0; y < this.currentPiece.shape.length; y++) {
                    for (let x = 0; x < this.currentPiece.shape[y].length; x++) {
                        if (this.currentPiece.shape[y][x]) {
                            const boardY = this.currentPiece.y + y;
                            const boardX = this.currentPiece.x + x;
                            
                            if (boardY >= 0) {
                                this.board[boardY][boardX] = this.currentPiece.color;
                            }
                        }
                    }
                }
            }
            
            // 清除完整的行
            clearLines() {
                let linesCleared = 0;
                
                for (let y = ROWS - 1; y >= 0; y--) {
                    if (this.board[y].every(cell => cell !== 0)) {
                        this.board.splice(y, 1);
                        this.board.unshift(Array(COLS).fill(0));
                        linesCleared++;
                        y++; // 重新检查当前行，因为上面的行下移了
                    }
                }
                
                if (linesCleared > 0) {
                    this.lines += linesCleared;
                    this.score += linesCleared * 100 * this.level;
                    
                    // 每清除10行提升一个等级
                    if (this.lines >= this.level * 10) {
                        this.level++;
                        this.dropInterval = Math.max(100, 1000 - (this.level - 1) * 100);
                    }
                    
                    this.updateScore();
                }
            }
            
            // 旋转方块
            rotate() {
                const rotated = [];
                const rows = this.currentPiece.shape.length;
                const cols = this.currentPiece.shape[0].length;
                
                for (let i = 0; i < cols; i++) {
                    rotated[i] = [];
                    for (let j = rows - 1; j >= 0; j--) {
                        rotated[i].push(this.currentPiece.shape[j][i]);
                    }
                }
                
                const prevShape = this.currentPiece.shape;
                this.currentPiece.shape = rotated;
                
                if (this.collision()) {
                    this.currentPiece.shape = prevShape;
                }
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
            
            // 硬降落（直接落到底部）
            hardDrop() {
                let dropDistance = 0;
                while (this.move(1)) {
                    dropDistance++;
                }
                this.score += dropDistance * 2;
                this.updateScore();
                this.lock();
            }
            
            // 锁定当前方块
            lock() {
                this.merge();
                this.clearLines();
                this.spawnPiece();
            }
            
            // 更新分数显示
            updateScore() {
                if (!this.isAI) {
                    document.getElementById('playerScore').textContent = this.score;
                    document.getElementById('playerLines').textContent = this.lines;
                    document.getElementById('playerLevel').textContent = this.level;
                } else {
                    document.getElementById('aiScore').textContent = this.score;
                    document.getElementById('aiLines').textContent = this.lines;
                    document.getElementById('aiLevel').textContent = this.level;
                }
            }
            
            // 更新下一个方块显示
            updateNextPieceDisplay() {
                const nextPieceDiv = document.getElementById('nextPiece');
                nextPieceDiv.innerHTML = '';
                
                for (let y = 0; y < 4; y++) {
                    for (let x = 0; x < 4; x++) {
                        const cell = document.createElement('div');
                        cell.className = 'next-piece-cell';
                        
                        if (this.nextPiece && 
                            y < this.nextPiece.shape.length && 
                            x < this.nextPiece.shape[0].length && 
                            this.nextPiece.shape[y][x]) {
                            cell.style.backgroundColor = this.nextPiece.color;
                        }
                        
                        nextPieceDiv.appendChild(cell);
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
                
                // 绘制游戏结束或暂停提示
                if (this.gameOver) {
                    this.ctx.fillStyle = 'rgba(0, 0, 0, 0.75)';
                    this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
                    
                    this.ctx.fillStyle = '#fff';
                    this.ctx.font = '30px Arial';
                    this.ctx.textAlign = 'center';
                    this.ctx.fillText('游戏结束', this.canvas.width / 2, this.canvas.height / 2);
                } else if (this.paused) {
                    this.ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
                    this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
                    
                    this.ctx.fillStyle = '#fff';
                    this.ctx.font = '30px Arial';
                    this.ctx.textAlign = 'center';
                    this.ctx.fillText('暂停', this.canvas.width / 2, this.canvas.height / 2);
                }
            }
            
            // 绘制网格
            drawGrid() {
                this.ctx.strokeStyle = '#222';
                this.ctx.lineWidth = 0.5;
                
                // 垂直线
                for (let x = 0; x <= COLS; x++) {
                    this.ctx.beginPath();
                    this.ctx.moveTo(x * BLOCK_SIZE, 0);
                    this.ctx.lineTo(x * BLOCK_SIZE, ROWS * BLOCK_SIZE);
                    this.ctx.stroke();
                }
                
                // 水平线
                for (let y = 0; y <= ROWS; y++) {
                    this.ctx.beginPath();
                    this.ctx.moveTo(0, y * BLOCK_SIZE);
                    this.ctx.lineTo(COLS * BLOCK_SIZE, y * BLOCK_SIZE);
                    this.ctx.stroke();
                }
            }
            
            // 绘制单个方块
            drawBlock(x, y, color) {
                this.ctx.fillStyle = color;
                this.ctx.fillRect(
                    x * BLOCK_SIZE + 1,
                    y * BLOCK_SIZE + 1,
                    BLOCK_SIZE - 2,
                    BLOCK_SIZE - 2
                );
                
                // 添加高光效果
                this.ctx.fillStyle = 'rgba(255, 255, 255, 0.3)';
                this.ctx.fillRect(
                    x * BLOCK_SIZE + 1,
                    y * BLOCK_SIZE + 1,
                    BLOCK_SIZE - 2,
                    4
                );
                
                // 添加阴影效果
                this.ctx.fillStyle = 'rgba(0, 0, 0, 0.3)';
                this.ctx.fillRect(
                    x * BLOCK_SIZE + 1,
                    y * BLOCK_SIZE + BLOCK_SIZE - 5,
                    BLOCK_SIZE - 2,
                    4
                );
            }
            
            // 游戏循环
            gameLoop(time = 0) {
                if (this.gameOver || this.paused) {
                    requestAnimationFrame((time) => this.gameLoop(time));
                    return;
                }
                
                const deltaTime = time - this.lastTime;
                this.lastTime = time;
                
               