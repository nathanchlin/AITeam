# 游戏UI界面开发

**Agent**: coder

**Time**: 2026-02-19T15:06:14.898317

---

我将为您创建一个完整的俄罗斯方块对战游戏界面，包含游戏画面、得分显示和控制面板。这将是一个单文件HTML应用，使用原生Canvas API实现。

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
            gap: 20px;
            padding: 20px;
            background-color: #16213e;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.5);
        }
        
        .game-board {
            position: relative;
        }
        
        canvas {
            border: 2px solid #0f3460;
            background-color: #0f3460;
            border-radius: 5px;
        }
        
        .side-panel {
            display: flex;
            flex-direction: column;
            gap: 20px;
            width: 200px;
        }
        
        .score-panel, .control-panel, .next-piece-panel {
            background-color: #0f3460;
            border-radius: 5px;
            padding: 15px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.3);
        }
        
        .score-panel h3, .control-panel h3, .next-piece-panel h3 {
            margin-bottom: 10px;
            color: #e94560;
            text-align: center;
        }
        
        .score {
            font-size: 24px;
            font-weight: bold;
            text-align: center;
            margin: 10px 0;
        }
        
        .next-piece-canvas {
            margin: 10px auto;
            display: block;
            background-color: #16213e;
            border: 1px solid #0f3460;
        }
        
        .control-button {
            width: 100%;
            padding: 10px;
            margin: 5px 0;
            background-color: #e94560;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            transition: background-color 0.3s;
        }
        
        .control-button:hover {
            background-color: #c13651;
        }
        
        .control-button:active {
            transform: scale(0.98);
        }
        
        .controls-info {
            margin-top: 15px;
            font-size: 14px;
            line-height: 1.6;
        }
        
        .controls-info kbd {
            background-color: #16213e;
            border: 1px solid #0f3460;
            border-radius: 3px;
            padding: 2px 5px;
            margin: 0 2px;
        }
        
        .game-over-overlay {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.7);
            display: none;
            justify-content: center;
            align-items: center;
            border-radius: 5px;
        }
        
        .game-over-message {
            background-color: #16213e;
            padding: 20px 40px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.5);
        }
        
        .game-over-message h2 {
            color: #e94560;
            margin-bottom: 15px;
        }
        
        .player-label {
            position: absolute;
            top: -30px;
            left: 0;
            width: 100%;
            text-align: center;
            font-size: 18px;
            font-weight: bold;
            color: #e94560;
        }
    </style>
</head>
<body>
    <div class="game-container">
        <div class="game-board">
            <div class="player-label">玩家</div>
            <canvas id="playerCanvas" width="300" height="600"></canvas>
            <div class="game-over-overlay" id="playerGameOver">
                <div class="game-over-message">
                    <h2>游戏结束!</h2>
                    <button class="control-button" onclick="resetGame()">重新开始</button>
                </div>
            </div>
        </div>
        
        <div class="side-panel">
            <div class="score-panel">
                <h3>得分</h3>
                <div class="score" id="playerScore">0</div>
                <div class="score" id="aiScore">0</div>
            </div>
            
            <div class="next-piece-panel">
                <h3>下一个方块</h3>
                <canvas id="nextPieceCanvas" class="next-piece-canvas" width="100" height="100"></canvas>
            </div>
            
            <div class="control-panel">
                <h3>控制</h3>
                <button class="control-button" id="startButton">开始游戏</button>
                <button class="control-button" id="pauseButton">暂停</button>
                <div class="controls-info">
                    <p><kbd>←</kbd> <kbd>→</kbd> 左右移动</p>
                    <p><kbd>↓</kbd> 加速下落</p>
                    <p><kbd>↑</kbd> 旋转</p>
                    <p><kbd>空格</kbd> 直接落下</p>
                </div>
            </div>
        </div>
        
        <div class="game-board">
            <div class="player-label">AI对手</div>
            <canvas id="aiCanvas" width="300" height="600"></canvas>
            <div class="game-over-overlay" id="aiGameOver">
                <div class="game-over-message">
                    <h2>AI失败!</h2>
                    <button class="control-button" onclick="resetGame()">重新开始</button>
                </div>
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
        
        // 游戏状态
        let gameState = {
            isRunning: false,
            isPaused: false,
            player: {
                board: [],
                currentPiece: null,
                nextPiece: null,
                score: 0,
                gameOver: false
            },
            ai: {
                board: [],
                currentPiece: null,
                nextPiece: null,
                score: 0,
                gameOver: false
            }
        };
        
        // 获取画布和上下文
        const playerCanvas = document.getElementById('playerCanvas');
        const aiCanvas = document.getElementById('aiCanvas');
        const nextPieceCanvas = document.getElementById('nextPieceCanvas');
        const playerCtx = playerCanvas.getContext('2d');
        const aiCtx = aiCanvas.getContext('2d');
        const nextPieceCtx = nextPieceCanvas.getContext('2d');
        
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
            gameState.player.board = Array(ROWS).fill().map(() => Array(COLS).fill(0));
            gameState.ai.board = Array(ROWS).fill().map(() => Array(COLS).fill(0));
        }
        
        // 随机生成新方块
        function randomPiece() {
            const shapeIndex = Math.floor(Math.random() * SHAPES.length);
            return new Piece(SHAPES[shapeIndex], COLORS[shapeIndex]);
        }
        
        // 检查碰撞
        function checkCollision(board, piece, dx = 0, dy = 0, newShape = null) {
            const shape = newShape || piece.shape;
            const newX = piece.x + dx;
            const newY = piece.y + dy;
            
            for (let y = 0; y < shape.length; y++) {
                for (let x = 0; x < shape[y].length; x++) {
                    if (shape[y][x]) {
                        const boardX = newX + x;
                        const boardY = newY + y;
                        
                        if (boardX < 0 || boardX >= COLS || boardY >= ROWS) {
                            return true;
                        }
                        
                        if (boardY >= 0 && board[boardY][boardX]) {
                            return true;
                        }
                    }
                }
            }
            
            return false;
        }
        
        // 合并方块到游戏板
        function mergePiece(board, piece) {
            for (let y = 0; y < piece.shape.length; y++) {
                for (let x = 0; x < piece.shape[y].length; x++) {
                    if (piece.shape[y][x]) {
                        const boardY = piece.y + y;
                        const boardX = piece.x + x;
                        
                        if (boardY >= 0) {
                            board[boardY][boardX] = piece.color;
                        }
                    }
                }
            }
        }
        
        // 清除完整的行
        function clearLines(board, player) {
            let linesCleared = 0;
            
            for (let y = ROWS - 1; y >= 0; y--) {
                if (board[y].every(cell => cell !== 0)) {
                    board.splice(y, 1);
                    board.unshift(Array(COLS).fill(0));
                    linesCleared++;
                    y++; // 重新检查当前行
                }
            }
            
            if (linesCleared > 0) {
                const points = [0, 40, 100, 300, 1200];
                gameState[player].score += points[linesCleared] * (gameState[player].level || 1);
                updateScore();
            }
            
            return linesCleared;
        }
        
        // 绘制游戏板
        function drawBoard(ctx, board) {
            ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
            
            // 绘制网格线
            ctx.strokeStyle = '#0a2443';
            ctx.lineWidth = 0.5;
            
            for (let i = 1; i < COLS; i++) {
                ctx.beginPath();
                ctx.moveTo(i * BLOCK_SIZE, 0);
                ctx.lineTo(i * BLOCK_SIZE, ROWS * BLOCK_SIZE);
                ctx.stroke();
            }
            
            for (let i = 1; i < ROWS; i++) {
                ctx.beginPath();
                ctx.moveTo(0, i * BLOCK_SIZE);
                ctx.lineTo(COLS * BLOCK_SIZE, i * BLOCK_SIZE);
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
        }
        
        // 绘制方块
        function drawBlock(ctx, x, y, color) {
            ctx.fillStyle = color;
            ctx.fillRect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE);
            
            // 添加高光效果
            ctx.fillStyle = 'rgba(255, 255, 255, 0.3)';
            ctx.fillRect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, 3);
            ctx.fillRect(x * BLOCK_SIZE, y * BLOCK_SIZE, 3, BLOCK_SIZE);
            
            // 添加阴影效果
            ctx.fillStyle = 'rgba(0, 0, 0, 0.3)';
            ctx.fillRect(x * BLOCK_SIZE + BLOCK_SIZE - 3, y * BLOCK_SIZE, 3, BLOCK_SIZE);
            ctx.fillRect(x * BLOCK_SIZE, y * BLOCK_SIZE + BLOCK_SIZE - 3, BLOCK_SIZE, 3);
        }
        
        // 绘制当前方块
        function drawPiece(ctx, piece) {
            if (!piece) return;
            
            for (let y = 0; y < piece.shape.length; y++) {
                for (let x = 0; x < piece.shape[y].length; x++) {
                    if (piece.shape[y][x]) {
                        drawBlock(ctx, piece.x + x, piece.y + y, piece.color);
                    }
                }
            }
        }
        
        // 绘制下一个方块
        function drawNextPiece(piece) {
            nextPieceCtx.clearRect(0, 0, nextPieceCanvas.width, nextPieceCanvas.height);
            
            if (!piece) return;
            
            const blockSize = 20;
            const offsetX = (nextPieceCanvas.width - piece.shape[0].length * blockSize) / 2;
            const offsetY = (nextPieceCanvas.height - piece.shape.length * blockSize) / 2;
            
            for (let y = 0; y < piece.shape.length; y++) {
                for (let x = 0; x < piece.shape[y].length; x++) {
                    if (piece.shape[y][x]) {
                        nextPieceCtx.fillStyle = piece.color;
                        nextPieceCtx.fillRect(
                            offsetX + x * blockSize,
                            offsetY + y * blockSize,
                            blockSize,
                            blockSize
                        );
                        
                        // 添加高光效果
                        nextPieceCtx.fillStyle = 'rgba(255, 255, 255, 0.3)';
                        nextPieceCtx.fillRect(
                            offsetX + x * blockSize,
                            offsetY + y * blockSize,
                            blockSize,
                            2
                        );
                        nextPieceCtx.fillRect(
                            offsetX + x * blockSize,
                            offsetY + y * blockSize,
                            2,
                            blockSize
                        );
                    }
                }
            }
        }
        
        // 更新分数显示
        function updateScore() {
            document.getElementById('playerScore').textContent = gameState.player.score;
            document.getElementById('aiScore').textContent = gameState.ai.score;
        }
        
        // 玩家移动方块
        function movePlayerPiece(dx, dy) {
            if (!gameState.isRunning || gameState.isPaused || gameState.player.gameOver) return;
            
            const piece = gameState.player.currentPiece;
            if (!checkCollision(gameState.player.board, piece, dx, dy)) {
                piece.x += dx;
                piece.y += dy;
                return true;
            }
            
            return false;
        }
        
        // 旋转玩家方块
        function rotatePlayerPiece() {
            if (!gameState.isRunning || gameState.isPaused || gameState.player.gameOver) return;
            
            const piece = gameState.player.currentPiece;
            const rotated = piece.rotate();
            
            if (!checkCollision(gameState.player.board, piece, 0, 0, rotated)) {
                piece.shape = rotated;
            }
        }
        
        // 硬降落（直接落到底部）
        function hardDropPlayerPiece() {
            if (!gameState.isRunning || gameState.isPaused || gameState.player.gameOver) return;
            
            const piece = gameState.player.currentPiece;
            while (movePlayerPiece(0, 1)) {
                // 继续下落直到碰撞
            }
        }
        
        // AI逻辑
        function aiMove() {
            if (!gameState.isRunning || gameState.isPaused || gameState.ai.gameOver) return;
            
            const piece = gameState.ai.currentPiece;
            const board = gameState.ai.board;
            
            // 简单的AI策略：找到最佳位置
            let bestX = 0;
            let bestRotation = 0;
            let bestScore = -Infinity;
            
            // 尝试所有可能的旋转和位置
            for (let rotation = 0; rotation < 4; rotation++) {
                const rotated = rotateMatrix(piece.shape, rotation);
                
                for (let x = 0; x < COLS; x++) {
                    // 模拟放置
                    let tempY = 0;
                    while (!checkCollision(board, {...piece, shape: rotated, x}, 0, tempY + 1)) {
                        tempY++;
                    }
                    
                    // 计算得分（简单的启发式）
                    let score = 0;
                    
                    // 鼓励填满底部
                    score += tempY * 10;
                    
                    // 鼓励消除行
                    const tempBoard = board.map(row => [...row]);
                    mergePiece(tempBoard, {...piece, shape: rotated, x, y: tempY});
                    const lines = clearLines(tempBoard, 'ai');
                    score += lines * 100;
                    
                    // 鼓励平整表面
                    const surfaceRoughness = calculateSurfaceRoughness(tempBoard);
                    score -= surfaceRoughness * 5;
                    
                    // 避免