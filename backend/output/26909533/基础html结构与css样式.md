# 基础HTML结构与CSS样式

**Agent**: coder

**Time**: 2026-02-17T17:13:43.732771

---

我将为你创建一个完整的俄罗斯方块游戏页面，包含HTML结构、CSS样式和JavaScript功能实现。下面是完整的代码：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>俄罗斯方块</title>
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
            background-color: #16213e;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.5);
        }
        
        .game-board {
            position: relative;
            width: 300px;
            height: 600px;
            background-color: #0f3460;
            border: 2px solid #e94560;
            box-shadow: inset 0 0 10px rgba(0, 0, 0, 0.3);
        }
        
        .game-info {
            display: flex;
            flex-direction: column;
            gap: 20px;
            min-width: 200px;
        }
        
        .info-box {
            background-color: #0f3460;
            padding: 15px;
            border-radius: 8px;
            border: 2px solid #e94560;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.3);
        }
        
        .info-box h2 {
            margin-bottom: 10px;
            color: #e94560;
            font-size: 18px;
            text-align: center;
        }
        
        .score {
            font-size: 24px;
            font-weight: bold;
            text-align: center;
            color: #f39c12;
        }
        
        .next-piece-container {
            width: 100px;
            height: 100px;
            margin: 0 auto;
            background-color: #0a2443;
            border: 1px solid #e94560;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        
        .next-piece {
            width: 80px;
            height: 80px;
            position: relative;
        }
        
        .controls {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        
        button {
            padding: 10px 20px;
            background-color: #e94560;
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        
        button:hover {
            background-color: #c13651;
        }
        
        button:active {
            transform: scale(0.98);
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
            z-index: 10;
        }
        
        .game-over h2 {
            color: #e94560;
            margin-bottom: 10px;
        }
        
        .game-over button {
            margin-top: 10px;
        }
        
        .instructions {
            font-size: 14px;
            line-height: 1.5;
        }
        
        .instructions h3 {
            color: #e94560;
            margin-bottom: 5px;
        }
        
        .instructions p {
            margin-bottom: 5px;
        }
        
        .cell {
            position: absolute;
            width: 30px;
            height: 30px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .cell.I {
            background-color: #00f0f0;
            box-shadow: 0 0 5px #00f0f0;
        }
        
        .cell.O {
            background-color: #f0f000;
            box-shadow: 0 0 5px #f0f000;
        }
        
        .cell.T {
            background-color: #a000f0;
            box-shadow: 0 0 5px #a000f0;
        }
        
        .cell.S {
            background-color: #00f000;
            box-shadow: 0 0 5px #00f000;
        }
        
        .cell.Z {
            background-color: #f00000;
            box-shadow: 0 0 5px #f00000;
        }
        
        .cell.J {
            background-color: #0000f0;
            box-shadow: 0 0 5px #0000f0;
        }
        
        .cell.L {
            background-color: #f0a000;
            box-shadow: 0 0 5px #f0a000;
        }
        
        .paused {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 24px;
            font-weight: bold;
            color: #e94560;
            display: none;
            z-index: 5;
        }
    </style>
</head>
<body>
    <div class="game-container">
        <div class="game-board" id="game-board">
            <div class="paused" id="paused">暂停中</div>
            <div class="game-over" id="game-over">
                <h2>游戏结束</h2>
                <p>最终得分: <span id="final-score">0</span></p>
                <button id="restart">重新开始</button>
            </div>
        </div>
        
        <div class="game-info">
            <div class="info-box">
                <h2>得分</h2>
                <div class="score" id="score">0</div>
            </div>
            
            <div class="info-box">
                <h2>下一个方块</h2>
                <div class="next-piece-container">
                    <div class="next-piece" id="next-piece"></div>
                </div>
            </div>
            
            <div class="info-box controls">
                <button id="start-pause">开始游戏</button>
                <button id="restart-btn">重新开始</button>
            </div>
            
            <div class="info-box instructions">
                <h3>操作说明</h3>
                <p>← → : 左右移动</p>
                <p>↑ : 旋转方块</p>
                <p>↓ : 加速下落</p>
                <p>空格 : 直接落下</p>
                <p>P : 暂停/继续</p>
            </div>
        </div>
    </div>

    <script>
        // 游戏配置
        const BOARD_WIDTH = 10;
        const BOARD_HEIGHT = 20;
        const CELL_SIZE = 30;
        
        // 方块形状定义
        const PIECES = {
            I: {
                shape: [
                    [0, 0, 0, 0],
                    [1, 1, 1, 1],
                    [0, 0, 0, 0],
                    [0, 0, 0, 0]
                ],
                color: 'I'
            },
            O: {
                shape: [
                    [1, 1],
                    [1, 1]
                ],
                color: 'O'
            },
            T: {
                shape: [
                    [0, 1, 0],
                    [1, 1, 1],
                    [0, 0, 0]
                ],
                color: 'T'
            },
            S: {
                shape: [
                    [0, 1, 1],
                    [1, 1, 0],
                    [0, 0, 0]
                ],
                color: 'S'
            },
            Z: {
                shape: [
                    [1, 1, 0],
                    [0, 1, 1],
                    [0, 0, 0]
                ],
                color: 'Z'
            },
            J: {
                shape: [
                    [1, 0, 0],
                    [1, 1, 1],
                    [0, 0, 0]
                ],
                color: 'J'
            },
            L: {
                shape: [
                    [0, 0, 1],
                    [1, 1, 1],
                    [0, 0, 0]
                ],
                color: 'L'
            }
        };
        
        // 游戏状态
        let board = [];
        let currentPiece = null;
        let nextPiece = null;
        let score = 0;
        let gameRunning = false;
        let gamePaused = false;
        let gameLoop = null;
        let dropCounter = 0;
        let lastTime = 0;
        
        // DOM 元素
        const gameBoard = document.getElementById('game-board');
        const scoreElement = document.getElementById('score');
        const nextPieceElement = document.getElementById('next-piece');
        const startPauseButton = document.getElementById('start-pause');
        const restartButton = document.getElementById('restart-btn');
        const gameOverElement = document.getElementById('game-over');
        const finalScoreElement = document.getElementById('final-score');
        const pausedElement = document.getElementById('paused');
        
        // 初始化游戏板
        function initBoard() {
            board = Array(BOARD_HEIGHT).fill(null).map(() => Array(BOARD_WIDTH).fill(0));
            clearBoard();
        }
        
        // 清空游戏板显示
        function clearBoard() {
            const cells = gameBoard.querySelectorAll('.cell');
            cells.forEach(cell => cell.remove());
        }
        
        // 渲染游戏板
        function renderBoard() {
            clearBoard();
            
            for (let y = 0; y < BOARD_HEIGHT; y++) {
                for (let x = 0; x < BOARD_WIDTH; x++) {
                    if (board[y][x]) {
                        const cell = document.createElement('div');
                        cell.className = `cell ${board[y][x]}`;
                        cell.style.left = `${x * CELL_SIZE}px`;
                        cell.style.top = `${y * CELL_SIZE}px`;
                        gameBoard.appendChild(cell);
                    }
                }
            }
            
            // 渲染当前方块
            if (currentPiece) {
                const { shape, color, x, y } = currentPiece;
                for (let row = 0; row < shape.length; row++) {
                    for (let col = 0; col < shape[row].length; col++) {
                        if (shape[row][col]) {
                            const cell = document.createElement('div');
                            cell.className = `cell ${color}`;
                            cell.style.left = `${(x + col) * CELL_SIZE}px`;
                            cell.style.top = `${(y + row) * CELL_SIZE}px`;
                            gameBoard.appendChild(cell);
                        }
                    }
                }
            }
        }
        
        // 渲染下一个方块
        function renderNextPiece() {
            nextPieceElement.innerHTML = '';
            
            if (nextPiece) {
                const { shape, color } = nextPiece;
                const cellSize = 20;
                
                for (let row = 0; row < shape.length; row++) {
                    for (let col = 0; col < shape[row].length; col++) {
                        if (shape[row][col]) {
                            const cell = document.createElement('div');
                            cell.className = `cell ${color}`;
                            cell.style.width = `${cellSize}px`;
                            cell.style.height = `${cellSize}px`;
                            cell.style.position = 'absolute';
                            cell.style.left = `${col * cellSize}px`;
                            cell.style.top = `${row * cellSize}px`;
                            nextPieceElement.appendChild(cell);
                        }
                    }
                }
            }
        }
        
        // 创建新方块
        function createPiece() {
            const pieces = Object.keys(PIECES);
            const randomPiece = pieces[Math.floor(Math.random() * pieces.length)];
            const piece = PIECES[randomPiece];
            
            return {
                shape: piece.shape,
                color: piece.color,
                x: Math.floor((BOARD_WIDTH - piece.shape[0].length) / 2),
                y: 0
            };
        }
        
        // 检查碰撞
        function checkCollision(piece, dx = 0, dy = 0, newShape = null) {
            const shape = newShape || piece.shape;
            
            for (let row = 0; row < shape.length; row++) {
                for (let col = 0; col < shape[row].length; col++) {
                    if (shape[row][col]) {
                        const newX = piece.x + col + dx;
                        const newY = piece.y + row + dy;
                        
                        if (
                            newX < 0 || 
                            newX >= BOARD_WIDTH || 
                            newY >= BOARD_HEIGHT ||
                            (newY >= 0 && board[newY][newX])
                        ) {
                            return true;
                        }
                    }
                }
            }
            
            return false;
        }
        
        // 旋转方块
        function rotatePiece(piece) {
            const rotated = [];
            const rows = piece.shape.length;
            const cols = piece.shape[0].length;
            
            for (let col = 0; col < cols; col++) {
                rotated[col] = [];
                for (let row = rows - 1; row >= 0; row--) {
                    rotated[col][rows - 1 - row] = piece.shape[row][col];
                }
            }
            
            return rotated;
        }
        
        // 锁定方块
        function lockPiece() {
            const { shape, color, x, y } = currentPiece;
            
            for (let row = 0; row < shape.length; row++) {
                for (let col = 0; col < shape[row].length; col++) {
                    if (shape[row][col]) {
                        if (y + row < 0) {
                            // 游戏结束
                            gameOver();
                            return;
                        }
                        board[y + row][x + col] = color;
                    }
                }
            }
            
            // 检查是否有完整的行
            checkLines();
            
            // 生成新方块
            currentPiece = nextPiece;
            nextPiece = createPiece();
            renderNextPiece();
            
            // 检查新方块是否立即碰撞
            if (checkCollision(currentPiece)) {
                gameOver();
            }
        }
        
        // 检查完整的行
        function checkLines() {
            let linesCleared = 0;
            
            for (let y = BOARD_HEIGHT - 1; y >= 0; y--) {
                if (board[y].every(cell => cell !== 0)) {
                    board.splice(y, 1);
                    board.unshift(Array(BOARD_WIDTH).fill(0));
                    linesCleared++;
                    y++; // 重新检查当前行，因为上面的行已经下移
                }
            }
            
            // 更新分数
            if (linesCleared > 0) {
                score += linesCleared * 100 * linesCleared; // 消除多行有额外奖励
                scoreElement.textContent = score;
            }
        }
        
        // 移动方块
        function movePiece(dx, dy) {
            if (!checkCollision(currentPiece, dx, dy)) {
                currentPiece.x += dx;
                currentPiece.y += dy;
                return true;
            }
            return false;
        }
        
        // 旋转当前方块
        function rotateCurrentPiece() {
            const rotated = rotatePiece(currentPiece);
            if (!checkCollision(currentPiece, 0, 0, rotated)) {
                currentPiece.shape = rotated;
            }
        }
        
        // 直接落下
        function hardDrop() {
            while (movePiece(0, 1)) {
                // 继续下落
            }
            lockPiece();
        }
        
        // 游戏循环
        function gameUpdate(time = 0) {
            if (!gameRunning || gamePaused) return;
            
            const deltaTime = time - lastTime;
            lastTime = time;
            dropCounter += deltaTime;
            
            if (dropCounter > 1000) { // 每秒下落一格
                if (!movePiece(0, 1)) {
                    lockPiece();
                }
                dropCounter = 0;
            }
            
            renderBoard();
            gameLoop = requestAnimationFrame(gameUpdate);
        }
        
        // 开始游戏
        function startGame() {
            if (gameRunning) return;
            
            initBoard();
            score = 0;
            scoreElement.textContent = score;
            gameRunning = true;
            gamePaused = false;
            startPauseButton.textContent = '暂停游戏';
            gameOverElement.style.display = 'none';
            
            currentPiece = createPiece();
            nextPiece = createPiece();
            renderNextPiece();
            
            lastTime = 0;
            dropCounter = 0;
            gameLoop = requestAnimationFrame(gameUpdate);
        }
        
        // 暂停/继续游戏
        function togglePause() {
            if (!gameRunning) return;
            
            gamePaused = !gamePaused;
            startPauseButton.textContent = gamePaused ? '继续游戏' : '暂停游戏';
            pausedElement.style.display = gamePaused ? 'block' : 'none';
            
            if (!gamePaused) {
                lastTime = 0;
                gameLoop = requestAnimationFrame(gameUpdate);
            }
        }
        
        // 游戏结束
        function gameOver() {
            gameRunning = false;
            cancelAnimationFrame(gameLoop);
            finalScoreElement.textContent = score;
            gameOverElement.style.display = 'block';
            startPauseButton.textContent = '开始游戏';
        }
        
        // 重新开始游戏
        function restartGame() {
            gameRunning = false;
            gamePaused = false;
            cancelAnimationFrame(gameLoop);
            startPauseButton.textContent = '开始游戏';
            gameOverElement.style.display = 'none';
            pausedElement.style.display = 'none';
            startGame();
        }
        
        // 键盘控制
        document.addEventListener('keydown', (e) => {
            if (!gameRunning || gamePaused) return;
            
            switch (e.key) {
                case 'ArrowLeft':
                    movePiece(-1, 0);
                    break;
                case 'ArrowRight':
