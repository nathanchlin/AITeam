# UI界面设计与实现

**Agent**: coder

**Time**: 2026-02-19T15:59:52.089468

---

我将为您创建一个完整的俄罗斯方块对战游戏UI界面。这个单文件HTML将包含游戏区域、得分显示、控制面板和游戏状态指示器，以及AI对手的实现。

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
            background-color: #111;
            color: #fff;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
        }
        
        .game-container {
            display: flex;
            gap: 30px;
            flex-wrap: wrap;
            justify-content: center;
            align-items: flex-start;
        }
        
        .game-board {
            position: relative;
            background-color: #222;
            border: 2px solid #444;
            border-radius: 5px;
            padding: 10px;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.5);
        }
        
        canvas {
            display: block;
            background-color: #000;
            border-radius: 3px;
        }
        
        .info-panel {
            background-color: #222;
            border: 2px solid #444;
            border-radius: 5px;
            padding: 20px;
            width: 200px;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.5);
        }
        
        .info-panel h2 {
            margin-bottom: 15px;
            color: #0ff;
            text-align: center;
            font-size: 18px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .score-display {
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 10px;
            text-align: center;
        }
        
        .level-display {
            font-size: 16px;
            margin-bottom: 20px;
            text-align: center;
            color: #ff0;
        }
        
        .control-panel {
            background-color: #222;
            border: 2px solid #444;
            border-radius: 5px;
            padding: 20px;
            width: 250px;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.5);
        }
        
        .control-panel h2 {
            margin-bottom: 15px;
            color: #0ff;
            text-align: center;
            font-size: 18px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .control-button {
            display: block;
            width: 100%;
            padding: 10px;
            margin-bottom: 10px;
            background-color: #444;
            color: #fff;
            border: none;
            border-radius: 3px;
            cursor: pointer;
            font-size: 16px;
            transition: background-color 0.2s;
        }
        
        .control-button:hover {
            background-color: #555;
        }
        
        .control-button:active {
            background-color: #333;
        }
        
        .control-button.primary {
            background-color: #0ff;
            color: #000;
        }
        
        .control-button.primary:hover {
            background-color: #0ee;
        }
        
        .game-status {
            text-align: center;
            margin-top: 20px;
            font-size: 18px;
            font-weight: bold;
            color: #0f0;
            min-height: 30px;
        }
        
        .game-status.game-over {
            color: #f00;
        }
        
        .game-status.paused {
            color: #ff0;
        }
        
        .next-piece {
            width: 80px;
            height: 80px;
            margin: 0 auto 15px;
            background-color: #000;
            border: 1px solid #444;
            border-radius: 3px;
        }
        
        .controls-info {
            margin-top: 20px;
            font-size: 14px;
            line-height: 1.6;
        }
        
        .controls-info h3 {
            margin-bottom: 10px;
            color: #0ff;
        }
        
        .controls-info p {
            margin-bottom: 5px;
        }
        
        .key {
            display: inline-block;
            background-color: #444;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: monospace;
            margin: 0 2px;
        }
        
        @media (max-width: 768px) {
            .game-container {
                flex-direction: column;
                align-items: center;
            }
            
            .info-panel, .control-panel {
                width: 100%;
                max-width: 300px;
            }
        }
    </style>
</head>
<body>
    <div class="game-container">
        <div class="game-board">
            <canvas id="playerCanvas" width="300" height="600"></canvas>
        </div>
        
        <div class="info-panel">
            <h2>玩家信息</h2>
            <div class="score-display" id="playerScore">0</div>
            <div class="level-display" id="playerLevel">等级: 1</div>
            <div class="next-piece">
                <canvas id="playerNextPiece" width="80" height="80"></canvas>
            </div>
        </div>
        
        <div class="game-board">
            <canvas id="aiCanvas" width="300" height="600"></canvas>
        </div>
        
        <div class="info-panel">
            <h2>对手信息</h2>
            <div class="score-display" id="aiScore">0</div>
            <div class="level-display" id="aiLevel">等级: 1</div>
            <div class="next-piece">
                <canvas id="aiNextPiece" width="80" height="80"></canvas>
            </div>
        </div>
        
        <div class="control-panel">
            <h2>游戏控制</h2>
            <button class="control-button primary" id="startBtn">开始游戏</button>
            <button class="control-button" id="pauseBtn">暂停</button>
            <button class="control-button" id="resetBtn">重置</button>
            
            <div class="game-status" id="gameStatus">准备开始</div>
            
            <div class="controls-info">
                <h3>操作说明</h3>
                <p><span class="key">←</span> <span class="key">→</span> 左右移动</p>
                <p><span class="key">↓</span> 加速下落</p>
                <p><span class="key">↑</span> 旋转方块</p>
                <p><span class="key">空格</span> 直接落下</p>
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
            [[1, 1, 1], [0, 1, 0]], // T
            [[1, 1, 1], [1, 0, 0]], // L
            [[1, 1, 1], [0, 0, 1]], // J
            [[0, 1, 1], [1, 1, 0]], // S
            [[1, 1, 0], [0, 1, 1]]  // Z
        ];
        
        // 游戏状态
        let gameState = {
            isRunning: false,
            isPaused: false,
            isGameOver: false,
            player: {
                board: [],
                score: 0,
                level: 1,
                lines: 0,
                currentPiece: null,
                nextPiece: null,
                dropInterval: 1000,
                lastDropTime: 0
            },
            ai: {
                board: [],
                score: 0,
                level: 1,
                lines: 0,
                currentPiece: null,
                nextPiece: null,
                dropInterval: 1000,
                lastDropTime: 0,
                difficulty: 1
            }
        };
        
        // 获取DOM元素
        const playerCanvas = document.getElementById('playerCanvas');
        const playerCtx = playerCanvas.getContext('2d');
        const aiCanvas = document.getElementById('aiCanvas');
        const aiCtx = aiCanvas.getContext('2d');
        const playerNextPieceCanvas = document.getElementById('playerNextPiece');
        const playerNextPieceCtx = playerNextPieceCanvas.getContext('2d');
        const aiNextPieceCanvas = document.getElementById('aiNextPiece');
        const aiNextPieceCtx = aiNextPieceCanvas.getContext('2d');
        
        // 控制按钮
        const startBtn = document.getElementById('startBtn');
        const pauseBtn = document.getElementById('pauseBtn');
        const resetBtn = document.getElementById('resetBtn');
        const gameStatus = document.getElementById('gameStatus');
        
        // 分数显示
        const playerScoreDisplay = document.getElementById('playerScore');
        const playerLevelDisplay = document.getElementById('playerLevel');
        const aiScoreDisplay = document.getElementById('aiScore');
        const aiLevelDisplay = document.getElementById('aiLevel');
        
        // 方块类
        class Piece {
            constructor(shape, color) {
                this.shape = shape;
                this.color = color;
                this.x = Math.floor((COLS - shape[0].length) / 2);
                this.y = 0;
            }
            
            rotate() {
                const rows = this.shape.length;
                const cols = this.shape[0].length;
                const rotated = [];
                
                for (let i = 0; i < cols; i++) {
                    rotated[i] = [];
                    for (let j = rows - 1; j >= 0; j--) {
                        rotated[i][rows - 1 - j] = this.shape[j][i];
                    }
                }
                
                return rotated;
            }
        }
        
        // 初始化游戏板
        function initBoard() {
            const board = [];
            for (let row = 0; row < ROWS; row++) {
                board[row] = [];
                for (let col = 0; col < COLS; col++) {
                    board[row][col] = 0;
                }
            }
            return board;
        }
        
        // 随机生成方块
        function randomPiece() {
            const shapeIndex = Math.floor(Math.random() * SHAPES.length);
            return new Piece(SHAPES[shapeIndex], COLORS[shapeIndex]);
        }
        
        // 检查碰撞
        function checkCollision(board, piece, dx = 0, dy = 0, newShape = null) {
            const shape = newShape || piece.shape;
            
            for (let row = 0; row < shape.length; row++) {
                for (let col = 0; col < shape[row].length; col++) {
                    if (shape[row][col]) {
                        const newX = piece.x + col + dx;
                        const newY = piece.y + row + dy;
                        
                        if (newX < 0 || newX >= COLS || newY >= ROWS) {
                            return true;
                        }
                        
                        if (newY >= 0 && board[newY][newX]) {
                            return true;
                        }
                    }
                }
            }
            
            return false;
        }
        
        // 将方块固定到游戏板
        function lockPiece(board, piece) {
            for (let row = 0; row < piece.shape.length; row++) {
                for (let col = 0; col < piece.shape[row].length; col++) {
                    if (piece.shape[row][col]) {
                        const boardY = piece.y + row;
                        const boardX = piece.x + col;
                        
                        if (boardY >= 0) {
                            board[boardY][boardX] = piece.color;
                        }
                    }
                }
            }
        }
        
        // 清除完整的行
        function clearLines(board) {
            let linesCleared = 0;
            
            for (let row = ROWS - 1; row >= 0; row--) {
                if (board[row].every(cell => cell !== 0)) {
                    board.splice(row, 1);
                    board.unshift(new Array(COLS).fill(0));
                    linesCleared++;
                    row++; // 重新检查当前行
                }
            }
            
            return linesCleared;
        }
        
        // 计算得分
        function calculateScore(linesCleared, level) {
            const linePoints = [0, 100, 300, 500, 800];
            return linePoints[linesCleared] * level;
        }
        
        // 更新游戏状态
        function updateGameState(player, linesCleared) {
            player.lines += linesCleared;
            player.score += calculateScore(linesCleared, player.level);
            
            // 每10行升一级
            const newLevel = Math.floor(player.lines / 10) + 1;
            if (newLevel > player.level) {
                player.level = newLevel;
                player.dropInterval = Math.max(100, 1000 - (player.level - 1) * 100);
            }
        }
        
        // 绘制游戏板
        function drawBoard(ctx, board) {
            ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
            
            // 绘制网格
            ctx.strokeStyle = '#333';
            ctx.lineWidth = 0.5;
            
            for (let row = 0; row < ROWS; row++) {
                for (let col = 0; col < COLS; col++) {
                    const x = col * BLOCK_SIZE;
                    const y = row * BLOCK_SIZE;
                    
                    ctx.strokeRect(x, y, BLOCK_SIZE, BLOCK_SIZE);
                    
                    if (board[row][col]) {
                        ctx.fillStyle = board[row][col];
                        ctx.fillRect(x, y, BLOCK_SIZE, BLOCK_SIZE);
                        
                        // 添加高光效果
                        ctx.fillStyle = 'rgba(255, 255, 255, 0.3)';
                        ctx.fillRect(x, y, BLOCK_SIZE / 3, BLOCK_SIZE / 3);
                    }
                }
            }
        }
        
        // 绘制方块
        function drawPiece(ctx, piece, offsetX = 0, offsetY = 0) {
            ctx.fillStyle = piece.color;
            
            for (let row = 0; row < piece.shape.length; row++) {
                for (let col = 0; col < piece.shape[row].length; col++) {
                    if (piece.shape[row][col]) {
                        const x = (piece.x + col) * BLOCK_SIZE + offsetX;
                        const y = (piece.y + row) * BLOCK_SIZE + offsetY;
                        
                        ctx.fillRect(x, y, BLOCK_SIZE, BLOCK_SIZE);
                        
                        // 添加高光效果
                        ctx.fillStyle = 'rgba(255, 255, 255, 0.3)';
                        ctx.fillRect(x, y, BLOCK_SIZE / 3, BLOCK_SIZE / 3);
                        ctx.fillStyle = piece.color;
                    }
                }
            }
        }
        
        // 绘制下一个方块
        function drawNextPiece(ctx, piece) {
            ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
            
            const blockSize = 20;
            const offsetX = (ctx.canvas.width - piece.shape[0].length * blockSize) / 2;
            const offsetY = (ctx.canvas.height - piece.shape.length * blockSize) / 2;
            
            ctx.fillStyle = piece.color;
            
            for (let row = 0; row < piece.shape.length; row++) {
                for (let col = 0; col < piece.shape[row].length; col++) {
                    if (piece.shape[row][col]) {
                        const x = col * blockSize + offsetX;
                        const y = row * blockSize + offsetY;
                        
                        ctx.fillRect(x, y, blockSize, blockSize);
                        
                        // 添加高光效果
                        ctx.fillStyle = 'rgba(255, 255, 255, 0.3)';
                        ctx.fillRect(x, y, blockSize / 3, blockSize / 3);
                        ctx.fillStyle = piece.color;
                    }
                }
            }
        }
        
        // 移动方块
        function movePiece(player, dx, dy) {
            if (!checkCollision(player.board, player.currentPiece, dx, dy)) {
                player.currentPiece.x += dx;
                player.currentPiece.y += dy;
                return true;
            }
            return false;
        }
        
        // 旋转方块
        function rotatePiece(player) {
            const rotated = player.currentPiece.rotate();
            
            if (!checkCollision(player.board, player.currentPiece, 0, 0, rotated)) {
                player.currentPiece.shape = rotated;
            }
        }
        
        // 硬降
        function hardDrop(player) {
            while (movePiece(player, 0, 1)) {
                // 继续下落
            }
        }
        
        // 生成新方块
        function spawnPiece(player) {
            player.currentPiece = player.nextPiece || randomPiece();
            player.nextPiece = randomPiece();
            
            if (checkCollision(player.board, player.currentPiece)) {
                return false; // 游戏结束
            }
            
            return true;
        }
        
        // AI决策
        function makeAIDecision(ai) {
            // 简单的AI策略：尝试找到最佳位置放置当前方块
            const possibleMoves = [];
            
            // 尝试所有可能的x位置
            for (let x = 0; x < COLS; x++) {
                // 尝试所有可能的旋转
                for (let rotation = 0; rotation < 4; rotation++) {
                    const testPiece = new Piece(
                        JSON.parse(JSON.stringify(ai.currentPiece.shape)),
                        ai.currentPiece.color
                    );
                    
                    // 应用旋转
                    for (let i = 