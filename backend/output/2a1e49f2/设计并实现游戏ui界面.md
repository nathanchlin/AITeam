# 设计并实现游戏UI界面

**Agent**: coder

**Time**: 2026-02-19T16:48:14.550055

---

我将为您设计并实现一个完整的俄罗斯方块对战游戏UI界面。这个界面将包含游戏区域、下一个方块预览、分数显示、控制按钮等元素，并实现响应式设计。

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
            background-color: #2c3e50;
            color: #ecf0f1;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
        }
        
        .game-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 20px;
            max-width: 1200px;
            width: 100%;
        }
        
        .game-header {
            text-align: center;
            width: 100%;
        }
        
        .game-title {
            font-size: 2.5rem;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
            background: linear-gradient(45deg, #3498db, #9b59b6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .game-content {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 30px;
            width: 100%;
        }
        
        .player-section {
            background-color: #34495e;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
            display: flex;
            flex-direction: column;
            align-items: center;
            min-width: 300px;
        }
        
        .player-title {
            font-size: 1.5rem;
            margin-bottom: 15px;
            color: #3498db;
        }
        
        .game-board {
            position: relative;
            border: 3px solid #3498db;
            border-radius: 5px;
            background-color: #1a252f;
            box-shadow: inset 0 0 10px rgba(0, 0, 0, 0.5);
        }
        
        canvas {
            display: block;
            background-color: #2c3e50;
        }
        
        .game-info {
            display: flex;
            flex-direction: column;
            gap: 15px;
            margin-top: 20px;
            width: 100%;
        }
        
        .info-box {
            background-color: #2c3e50;
            border-radius: 5px;
            padding: 10px;
            text-align: center;
            border: 1px solid #3498db;
        }
        
        .info-label {
            font-size: 0.9rem;
            color: #95a5a6;
            margin-bottom: 5px;
        }
        
        .info-value {
            font-size: 1.5rem;
            font-weight: bold;
            color: #3498db;
        }
        
        .next-piece-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 10px;
        }
        
        .next-piece-label {
            font-size: 1rem;
            color: #95a5a6;
        }
        
        .next-piece-canvas {
            border: 2px solid #3498db;
            border-radius: 5px;
            background-color: #1a252f;
        }
        
        .controls {
            display: flex;
            flex-direction: column;
            gap: 10px;
            margin-top: 20px;
        }
        
        .control-buttons {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 5px;
            width: 150px;
        }
        
        .control-btn {
            background-color: #3498db;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 10px;
            font-size: 1rem;
            cursor: pointer;
            transition: background-color 0.2s;
        }
        
        .control-btn:hover {
            background-color: #2980b9;
        }
        
        .control-btn:active {
            background-color: #21618c;
            transform: scale(0.98);
        }
        
        .control-btn:nth-child(2) {
            grid-column: 2;
        }
        
        .control-btn:nth-child(4) {
            grid-column: 1;
        }
        
        .control-btn:nth-child(5) {
            grid-column: 2;
        }
        
        .control-btn:nth-child(6) {
            grid-column: 3;
        }
        
        .control-btn:nth-child(7) {
            grid-column: 2;
        }
        
        .game-controls {
            display: flex;
            gap: 10px;
            margin-top: 10px;
        }
        
        .game-btn {
            background-color: #2ecc71;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 10px 20px;
            font-size: 1rem;
            cursor: pointer;
            transition: background-color 0.2s;
        }
        
        .game-btn:hover {
            background-color: #27ae60;
        }
        
        .game-btn.pause {
            background-color: #f39c12;
        }
        
        .game-btn.pause:hover {
            background-color: #e67e22;
        }
        
        .game-btn.reset {
            background-color: #e74c3c;
        }
        
        .game-btn.reset:hover {
            background-color: #c0392b;
        }
        
        .game-status {
            font-size: 1.2rem;
            margin-top: 10px;
            height: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .status-playing {
            color: #2ecc71;
        }
        
        .status-paused {
            color: #f39c12;
        }
        
        .status-gameover {
            color: #e74c3c;
        }
        
        .ai-section {
            background-color: #8e44ad;
            padding: 10px;
            border-radius: 5px;
            margin-top: 10px;
            width: 100%;
            text-align: center;
        }
        
        .ai-label {
            font-size: 0.9rem;
            margin-bottom: 5px;
        }
        
        .ai-level {
            font-size: 1.2rem;
            font-weight: bold;
        }
        
        @media (max-width: 768px) {
            .game-content {
                flex-direction: column;
            }
            
            .player-section {
                min-width: 280px;
            }
            
            .game-title {
                font-size: 2rem;
            }
            
            .control-buttons {
                width: 120px;
            }
            
            .control-btn {
                padding: 8px;
                font-size: 0.9rem;
            }
        }
    </style>
</head>
<body>
    <div class="game-container">
        <header class="game-header">
            <h1 class="game-title">俄罗斯方块对战</h1>
        </header>
        
        <div class="game-content">
            <!-- 玩家区域 -->
            <div class="player-section">
                <h2 class="player-title">玩家</h2>
                <div class="game-board">
                    <canvas id="player-canvas" width="300" height="600"></canvas>
                </div>
                
                <div class="game-info">
                    <div class="info-box">
                        <div class="info-label">分数</div>
                        <div class="info-value" id="player-score">0</div>
                    </div>
                    
                    <div class="info-box">
                        <div class="info-label">等级</div>
                        <div class="info-value" id="player-level">1</div>
                    </div>
                    
                    <div class="info-box">
                        <div class="info-label">消除行数</div>
                        <div class="info-value" id="player-lines">0</div>
                    </div>
                    
                    <div class="next-piece-container">
                        <div class="next-piece-label">下一个方块</div>
                        <canvas id="player-next-canvas" class="next-piece-canvas" width="120" height="80"></canvas>
                    </div>
                </div>
                
                <div class="controls">
                    <div class="control-buttons">
                        <button class="control-btn" id="player-rotate">↻</button>
                        <button class="control-btn" id="player-left">←</button>
                        <button class="control-btn" id="player-down">↓</button>
                        <button class="control-btn" id="player-right">→</button>
                        <button class="control-btn" id="player-drop">↓</button>
                    </div>
                    
                    <div class="game-controls">
                        <button class="game-btn" id="player-start">开始</button>
                        <button class="game-btn pause" id="player-pause">暂停</button>
                        <button class="game-btn reset" id="player-reset">重置</button>
                    </div>
                    
                    <div class="game-status" id="player-status">准备就绪</div>
                </div>
            </div>
            
            <!-- AI区域 -->
            <div class="player-section">
                <h2 class="player-title">AI对手</h2>
                <div class="game-board">
                    <canvas id="ai-canvas" width="300" height="600"></canvas>
                </div>
                
                <div class="game-info">
                    <div class="info-box">
                        <div class="info-label">分数</div>
                        <div class="info-value" id="ai-score">0</div>
                    </div>
                    
                    <div class="info-box">
                        <div class="info-label">等级</div>
                        <div class="info-value" id="ai-level">1</div>
                    </div>
                    
                    <div class="info-box">
                        <div class="info-label">消除行数</div>
                        <div class="info-value" id="ai-lines">0</div>
                    </div>
                    
                    <div class="next-piece-container">
                        <div class="next-piece-label">下一个方块</div>
                        <canvas id="ai-next-canvas" class="next-piece-canvas" width="120" height="80"></canvas>
                    </div>
                </div>
                
                <div class="ai-section">
                    <div class="ai-label">AI难度</div>
                    <div class="ai-level" id="ai-level-display">中等</div>
                </div>
                
                <div class="game-controls">
                    <button class="game-btn" id="ai-start">开始</button>
                    <button class="game-btn pause" id="ai-pause">暂停</button>
                    <button class="game-btn reset" id="ai-reset">重置</button>
                </div>
                
                <div class="game-status" id="ai-status">准备就绪</div>
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
            [[1, 1, 0, 0], [1, 1, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]], // O
            [[0, 1, 0, 0], [1, 1, 1, 0], [0, 0, 0, 0], [0, 0, 0, 0]], // T
            [[0, 0, 1, 0], [1, 1, 1, 0], [0, 0, 0, 0], [0, 0, 0, 0]], // L
            [[0, 1, 1, 0], [1, 1, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]], // J
            [[0, 1, 1, 0], [1, 1, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]], // S
            [[0, 0, 1, 1], [0, 1, 1, 0], [0, 0, 0, 0], [0, 0, 0, 0]]  // Z
        ];
        
        // 游戏状态
        class GameState {
            constructor(canvasId, nextCanvasId, scoreId, levelId, linesId, statusId) {
                this.canvas = document.getElementById(canvasId);
                this.ctx = this.canvas.getContext('2d');
                this.nextCanvas = document.getElementById(nextCanvasId);
                this.nextCtx = this.nextCanvas.getContext('2d');
                this.scoreElement = document.getElementById(scoreId);
                this.levelElement = document.getElementById(levelId);
                this.linesElement = document.getElementById(linesId);
                this.statusElement = document.getElementById(statusId);
                
                this.board = this.createBoard();
                this.currentPiece = null;
                this.nextPiece = null;
                this.score = 0;
                this.level = 1;
                this.lines = 0;
                this.gameOver = false;
                this.paused = false;
                this.dropCounter = 0;
                this.lastTime = 0;
                this.dropInterval = 1000; // 1秒
                
                this.init();
            }
            
            createBoard() {
                return Array(ROWS).fill().map(() => Array(COLS).fill(0));
            }
            
            init() {
                this.currentPiece = this.createPiece();
                this.nextPiece = this.createPiece();
                this.draw();
                this.drawNext();
            }
            
            createPiece() {
                const typeId = Math.floor(Math.random() * SHAPES.length);
                return {
                    x: Math.floor(COLS / 2) - 2,
                    y: 0,
                    type: typeId,
                    shape: SHAPES[typeId],
                    color: COLORS[typeId]
                };
            }
            
            rotate(piece) {
                // 旋转矩阵
                const rotated = piece.shape.map((row, i) => 
                    piece.shape.map(col => row[col]).reverse()
                );
                
                // 检查旋转后是否有效
                const newPiece = {
                    ...piece,
                    shape: rotated
                };
                
                if (this.validMove(newPiece)) {
                    return newPiece;
                }
                
                return piece;
            }
            
            validMove(piece) {
                for (let y = 0; y < piece.shape.length; y++) {
                    for (let x = 0; x < piece.shape[y].length; x++) {
                        if (piece.shape[y][x] !== 0) {
                            const newX = piece.x + x;
                            const newY = piece.y + y;
                            
                            if (newX < 0 || newX >= COLS || newY >= ROWS) {
                                return false;
                            }
                            
                            if (newY >= 0 && this.board[newY][newX] !== 0) {
                                return false;
                            }
                        }
                    }
                }
                return true;
            }
            
            merge() {
                this.currentPiece.shape.forEach((row, y) => {
                    row.forEach((value, x) => {
                        if (value !== 0) {
                            const boardY = this.currentPiece.y + y;
                            const boardX = this.currentPiece.x + x;
                            if (boardY >= 0) {
                                this.board[boardY][boardX] = this.currentPiece.type + 1;
                            }
                        }
                    });
                });
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
                    this.score += linesCleared * 100 * this.level;
                    this.level = Math.floor(this.lines / 10) + 1;
                    this.dropInterval = Math.max(100, 1000 - (this.level - 1) * 100);
                    
                    this.updateUI();
                }
            }
            
            drop() {
                this.currentPiece.y++;
                if (!this.validMove(this.currentPiece)) {
                    this.currentPiece.y--;
                    this.merge();
                    this.clearLines();
                    this.currentPiece = this.nextPiece;
                    this.nextPiece = this.createPiece();
                    
                    if (!this.validMove(this.currentPiece)) {
                        this.gameOver = true;
                        this.statusElement.textContent = '游戏结束';
                        this.statusElement.className = 'game-status status-gameover';
                    }
                    
                    this.drawNext();
                }
                this.dropCounter = 0;
            }
            
            hardDrop() {
                while (this.validMove({...this.currentPiece, y: this.currentPiece.y + 1})) {
                    this.currentPiece.y++;
                    this.score += 2;
                }
                this.drop();
                this.updateUI();
            }
            
            move(dir) {
                this.currentPiece.x += dir;
                if (!this.validMove(this