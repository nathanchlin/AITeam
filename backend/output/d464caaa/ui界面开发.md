# UI界面开发

**Agent**: coder

**Time**: 2026-02-19T15:16:14.236584

---

我将为您开发一个完整的俄罗斯方块对战游戏界面，包含游戏区域、控制面板和状态显示等UI组件。这个单文件HTML将包含所有必要的CSS和JavaScript代码，可以直接在浏览器中运行。

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
            padding: 20px;
        }
        
        .game-container {
            display: flex;
            gap: 30px;
            background-color: #16213e;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        }
        
        .game-area {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        
        .player-section {
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        
        .player-title {
            font-size: 24px;
            margin-bottom: 10px;
            color: #f39c12;
        }
        
        .game-board {
            border: 3px solid #34495e;
            border-radius: 8px;
            background-color: #2c3e50;
        }
        
        .info-panel {
            background-color: #0f3460;
            border-radius: 8px;
            padding: 15px;
            width: 200px;
            margin-top: 10px;
        }
        
        .info-item {
            margin-bottom: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .info-label {
            font-size: 14px;
            color: #95a5a6;
        }
        
        .info-value {
            font-size: 18px;
            font-weight: bold;
            color: #f39c12;
        }
        
        .next-piece {
            margin-top: 15px;
            text-align: center;
        }
        
        .next-canvas {
            border: 1px solid #34495e;
            background-color: #2c3e50;
            margin-top: 5px;
        }
        
        .controls {
            background-color: #0f3460;
            border-radius: 8px;
            padding: 20px;
            width: 250px;
        }
        
        .controls h3 {
            margin-bottom: 15px;
            color: #f39c12;
            text-align: center;
        }
        
        .control-group {
            margin-bottom: 15px;
        }
        
        .control-label {
            font-size: 14px;
            margin-bottom: 5px;
            color: #95a5a6;
        }
        
        .control-keys {
            display: flex;
            gap: 5px;
            justify-content: center;
        }
        
        .key {
            background-color: #34495e;
            border: 1px solid #4a5f7a;
            border-radius: 4px;
            padding: 5px 10px;
            font-size: 12px;
            min-width: 30px;
            text-align: center;
        }
        
        .button-group {
            display: flex;
            flex-direction: column;
            gap: 10px;
            margin-top: 20px;
        }
        
        .game-button {
            background-color: #e74c3c;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 10px 15px;
            font-size: 16px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        
        .game-button:hover {
            background-color: #c0392b;
        }
        
        .game-button:active {
            transform: scale(0.98);
        }
        
        .game-button.start {
            background-color: #27ae60;
        }
        
        .game-button.start:hover {
            background-color: #229954;
        }
        
        .game-over-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.8);
            display: none;
            justify-content: center;
            align-items: center;
            z-index: 1000;
        }
        
        .game-over-content {
            background-color: #16213e;
            border-radius: 15px;
            padding: 30px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        }
        
        .game-over-title {
            font-size: 36px;
            margin-bottom: 20px;
            color: #e74c3c;
        }
        
        .game-over-message {
            font-size: 20px;
            margin-bottom: 30px;
        }
        
        .attack-indicator {
            position: absolute;
            top: 10px;
            right: 10px;
            background-color: #e74c3c;
            color: white;
            padding: 5px 10px;
            border-radius: 5px;
            font-weight: bold;
            display: none;
            animation: pulse 0.5s infinite;
        }
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.1); }
            100% { transform: scale(1); }
        }
    </style>
</head>
<body>
    <div class="game-container">
        <div class="game-area">
            <div class="player-section">
                <h2 class="player-title">玩家</h2>
                <div style="position: relative;">
                    <canvas id="playerBoard" class="game-board" width="300" height="600"></canvas>
                    <div id="playerAttackIndicator" class="attack-indicator">攻击!</div>
                </div>
                <div class="info-panel">
                    <div class="info-item">
                        <span class="info-label">分数:</span>
                        <span id="playerScore" class="info-value">0</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">等级:</span>
                        <span id="playerLevel" class="info-value">1</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">消除行数:</span>
                        <span id="playerLines" class="info-value">0</span>
                    </div>
                    <div class="next-piece">
                        <div class="info-label">下一个方块:</div>
                        <canvas id="playerNext" class="next-canvas" width="100" height="80"></canvas>
                    </div>
                </div>
            </div>
            
            <div class="player-section">
                <h2 class="player-title">AI对手</h2>
                <div style="position: relative;">
                    <canvas id="aiBoard" class="game-board" width="300" height="600"></canvas>
                    <div id="aiAttackIndicator" class="attack-indicator">攻击!</div>
                </div>
                <div class="info-panel">
                    <div class="info-item">
                        <span class="info-label">分数:</span>
                        <span id="aiScore" class="info-value">0</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">等级:</span>
                        <span id="aiLevel" class="info-value">1</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">消除行数:</span>
                        <span id="aiLines" class="info-value">0</span>
                    </div>
                    <div class="next-piece">
                        <div class="info-label">下一个方块:</div>
                        <canvas id="aiNext" class="next-canvas" width="100" height="80"></canvas>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="controls">
            <h3>游戏控制</h3>
            
            <div class="control-group">
                <div class="control-label">移动:</div>
                <div class="control-keys">
                    <div class="key">←</div>
                    <div class="key">→</div>
                </div>
            </div>
            
            <div class="control-group">
                <div class="control-label">旋转:</div>
                <div class="control-keys">
                    <div class="key">↑</div>
                </div>
            </div>
            
            <div class="control-group">
                <div class="control-label">快速下落:</div>
                <div class="control-keys">
                    <div class="key">↓</div>
                </div>
            </div>
            
            <div class="control-group">
                <div class="control-label">直接落下:</div>
                <div class="control-keys">
                    <div class="key">空格</div>
                </div>
            </div>
            
            <div class="button-group">
                <button id="startButton" class="game-button start">开始游戏</button>
                <button id="pauseButton" class="game-button">暂停</button>
                <button id="resetButton" class="game-button">重置</button>
            </div>
        </div>
    </div>
    
    <div id="gameOverOverlay" class="game-over-overlay">
        <div class="game-over-content">
            <h2 id="gameOverTitle" class="game-over-title">游戏结束</h2>
            <p id="gameOverMessage" class="game-over-message">你输了!</p>
            <button id="restartButton" class="game-button start">再来一局</button>
        </div>
    </div>
    
    <script>
        // 游戏常量
        const BOARD_WIDTH = 10;
        const BOARD_HEIGHT = 20;
        const CELL_SIZE = 30;
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
                level: 1,
                lines: 0,
                dropInterval: 1000,
                lastDropTime: 0
            },
            ai: {
                board: [],
                currentPiece: null,
                nextPiece: null,
                score: 0,
                level: 1,
                lines: 0,
                dropInterval: 1000,
                lastDropTime: 0
            }
        };
        
        // Canvas元素
        const playerCanvas = document.getElementById('playerBoard');
        const playerCtx = playerCanvas.getContext('2d');
        const aiCanvas = document.getElementById('aiBoard');
        const aiCtx = aiCanvas.getContext('2d');
        const playerNextCanvas = document.getElementById('playerNext');
        const playerNextCtx = playerNextCanvas.getContext('2d');
        const aiNextCanvas = document.getElementById('aiNext');
        const aiNextCtx = aiNextCanvas.getContext('2d');
        
        // 初始化游戏板
        function initializeBoard() {
            gameState.player.board = Array(BOARD_HEIGHT).fill().map(() => Array(BOARD_WIDTH).fill(0));
            gameState.ai.board = Array(BOARD_HEIGHT).fill().map(() => Array(BOARD_WIDTH).fill(0));
        }
        
        // 创建新方块
        function createPiece() {
            const shapeIndex = Math.floor(Math.random() * SHAPES.length);
            return {
                shape: SHAPES[shapeIndex],
                color: COLORS[shapeIndex],
                x: Math.floor((BOARD_WIDTH - SHAPES[shapeIndex][0].length) / 2),
                y: 0
            };
        }
        
        // 检查碰撞
        function checkCollision(board, piece, dx = 0, dy = 0) {
            for (let y = 0; y < piece.shape.length; y++) {
                for (let x = 0; x < piece.shape[y].length; x++) {
                    if (piece.shape[y][x]) {
                        const newX = piece.x + x + dx;
                        const newY = piece.y + y + dy;
                        
                        if (newX < 0 || newX >= BOARD_WIDTH || 
                            newY >= BOARD_HEIGHT || 
                            (newY >= 0 && board[newY][newX])) {
                            return true;
                        }
                    }
                }
            }
            return false;
        }
        
        // 固定方块到游戏板
        function lockPiece(board, piece) {
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
        
        // 旋转方块
        function rotatePiece(piece) {
            const rotated = [];
            const rows = piece.shape.length;
            const cols = piece.shape[0].length;
            
            for (let i = 0; i < cols; i++) {
                rotated[i] = [];
                for (let j = rows - 1; j >= 0; j--) {
                    rotated[i][rows - 1 - j] = piece.shape[j][i];
                }
            }
            
            return {
                ...piece,
                shape: rotated
            };
        }
        
        // 检查并清除完整的行
        function clearLines(board) {
            let linesCleared = 0;
            
            for (let y = BOARD_HEIGHT - 1; y >= 0; y--) {
                if (board[y].every(cell => cell !== 0)) {
                    board.splice(y, 1);
                    board.unshift(Array(BOARD_WIDTH).fill(0));
                    linesCleared++;
                    y++; // 重新检查当前行
                }
            }
            
            return linesCleared;
        }
        
        // 更新分数
        function updateScore(player, linesCleared) {
            const points = [0, 100, 300, 500, 800];
            player.score += points[linesCleared] * player.level;
            player.lines += linesCleared;
            player.level = Math.floor(player.lines / 10) + 1;
            player.dropInterval = Math.max(100, 1000 - (player.level - 1) * 100);
            
            // 更新UI
            document.getElementById(`${player === gameState.player ? 'player' : 'ai'}Score`).textContent = player.score;
            document.getElementById(`${player === gameState.player ? 'player' : 'ai'}Level`).textContent = player.level;
            document.getElementById(`${player === gameState.player ? 'player' : 'ai'}Lines`).textContent = player.lines;
        }
        
        // 发送攻击行
        function sendAttackLines(fromPlayer, toPlayer, count) {
            const attackLines = Array(BOARD_WIDTH).fill(0);
            for (let i = 1; i < BOARD_WIDTH - 1; i++) {
                attackLines[i] = fromPlayer === gameState.player ? COLORS[Math.floor(Math.random() * COLORS.length)] : '#888';
            }
            
            // 移除顶部的行
            toPlayer.board.splice(0, count);
            
            // 添加攻击行到底部
            for (let i = 0; i < count; i++) {
                toPlayer.board.push(attackLines);
            }
            
            // 显示攻击指示器
            const indicator = document.getElementById(`${toPlayer === gameState.player ? 'player' : 'ai'}AttackIndicator`);
            indicator.style.display = 'block';
            setTimeout(() => {
                indicator.style.display = 'none';
            }, 1000);
        }
        
        // 绘制游戏板
        function drawBoard(ctx, board) {
            ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
            
            // 绘制网格
            ctx.strokeStyle = '#34495e';
            ctx.lineWidth = 0.5;
            
            for (let x = 0; x <= BOARD_WIDTH; x++) {
                ctx.beginPath();
                ctx.moveTo(x * CELL_SIZE, 0);
                ctx.lineTo(x * CELL_SIZE, BOARD_HEIGHT * CELL_SIZE);
                ctx.stroke();
            }
            
            for (let y = 0; y <= BOARD_HEIGHT; y++) {
                ctx.beginPath();
                ctx.moveTo(0, y * CELL_SIZE);
                ctx.lineTo(BOARD_WIDTH * CELL_SIZE, y * CELL_SIZE);
                ctx.stroke();
            }
            
            // 绘制已固定的方块
            for (let y = 0; y < BOARD_HEIGHT; y++) {
                for (let x = 0; x < BOARD_WIDTH; x++) {
                    if (board[y][x]) {
                        drawCell(ctx, x, y, board[y][x]);
                    }
                }
            }
        }
        
        // 绘制方块
        function drawCell(ctx, x, y, color) {
            ctx.fillStyle = color;
            ctx.fillRect(x * CELL_SIZE, y