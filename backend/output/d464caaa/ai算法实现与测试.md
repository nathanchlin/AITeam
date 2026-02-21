# AI算法实现与测试

**Agent**: coder

**Time**: 2026-02-19T15:13:50.499049

---

我将为您创建一个完整的俄罗斯方块对战游戏，包含AI对手。这个实现将包括游戏逻辑、AI算法和完整的用户界面。

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>俄罗斯方块对战 - AI版</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background-color: #1a1a2e;
            font-family: 'Arial', sans-serif;
            color: #eee;
        }
        
        .game-container {
            display: flex;
            gap: 20px;
            padding: 20px;
            background-color: #16213e;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.5);
        }
        
        .game-area {
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        
        canvas {
            border: 2px solid #0f3460;
            background-color: #0f3460;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.3);
        }
        
        .info-panel {
            margin-top: 10px;
            text-align: center;
        }
        
        .score {
            font-size: 18px;
            margin: 5px 0;
        }
        
        .controls {
            margin-top: 20px;
            text-align: center;
            background-color: #0f3460;
            padding: 15px;
            border-radius: 5px;
            width: 300px;
        }
        
        .controls h3 {
            margin-top: 0;
            color: #e94560;
        }
        
        .control-item {
            margin: 5px 0;
            display: flex;
            justify-content: space-between;
        }
        
        .key {
            background-color: #e94560;
            color: white;
            padding: 2px 8px;
            border-radius: 3px;
            font-weight: bold;
        }
        
        .game-status {
            text-align: center;
            margin: 10px 0;
            font-size: 20px;
            font-weight: bold;
        }
        
        .start-button {
            background-color: #e94560;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        
        .start-button:hover {
            background-color: #c13651;
        }
        
        .ai-level {
            margin: 10px 0;
        }
        
        .ai-level select {
            background-color: #0f3460;
            color: white;
            border: 1px solid #e94560;
            padding: 5px;
            border-radius: 3px;
        }
    </style>
</head>
<body>
    <div class="game-container">
        <div class="game-area">
            <h3>玩家</h3>
            <canvas id="playerCanvas" width="300" height="600"></canvas>
            <div class="info-panel">
                <div class="score">分数: <span id="playerScore">0</span></div>
                <div class="score">消除行数: <span id="playerLines">0</span></div>
                <div class="score">等级: <span id="playerLevel">1</span></div>
            </div>
        </div>
        
        <div class="game-area">
            <h3>AI对手</h3>
            <canvas id="aiCanvas" width="300" height="600"></canvas>
            <div class="info-panel">
                <div class="score">分数: <span id="aiScore">0</span></div>
                <div class="score">消除行数: <span id="aiLines">0</span></div>
                <div class="score">等级: <span id="aiLevel">1</span></div>
            </div>
        </div>
    </div>
    
    <div class="controls">
        <h3>游戏控制</h3>
        <div class="control-item">
            <span>左移</span>
            <span class="key">←</span>
        </div>
        <div class="control-item">
            <span>右移</span>
            <span class="key">→</span>
        </div>
        <div class="control-item">
            <span>旋转</span>
            <span class="key">↑</span>
        </div>
        <div class="control-item">
            <span>快速下落</span>
            <span class="key">↓</span>
        </div>
        <div class="control-item">
            <span>直接落下</span>
            <span class="key">空格</span>
        </div>
        
        <div class="ai-level">
            <label for="aiDifficulty">AI难度: </label>
            <select id="aiDifficulty">
                <option value="easy">简单</option>
                <option value="medium" selected>中等</option>
                <option value="hard">困难</option>
            </select>
        </div>
        
        <button class="start-button" id="startButton">开始游戏</button>
        <div class="game-status" id="gameStatus">按"开始游戏"开始</div>
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
            '#FF0D72', // 粉色 - I
            '#0DC2FF', // 蓝色 - J
            '#0DFF72', // 绿色 - L
            '#F538FF', // 紫色 - O
            '#FF8E0D', // 橙色 - S
            '#FFE138', // 黄色 - T
            '#3877FF'  // 深蓝 - Z
        ];
        
        // 方块类
        class Piece {
            constructor(shape, color) {
                this.shape = shape;
                this.color = color;
                this.x = Math.floor((COLS - shape[0].length) / 2);
                this.y = 0;
            }
            
            // 旋转方块
            rotate() {
                const rotated = [];
                const rows = this.shape.length;
                const cols = this.shape[0].length;
                
                for (let i = 0; i < cols; i++) {
                    rotated[i] = [];
                    for (let j = rows - 1; j >= 0; j--) {
                        rotated[i][rows - 1 - j] = this.shape[j][i];
                    }
                }
                
                return rotated;
            }
        }
        
        // 游戏板类
        class Board {
            constructor(canvasId, isAI = false) {
                this.canvas = document.getElementById(canvasId);
                this.ctx = this.canvas.getContext('2d');
                this.isAI = isAI;
                this.grid = Array(ROWS).fill().map(() => Array(COLS).fill(0));
                this.currentPiece = null;
                this.score = 0;
                this.lines = 0;
                this.level = 1;
                this.gameOver = false;
                this.dropCounter = 0;
                this.dropInterval = 1000;
                this.lastTime = 0;
                
                // AI相关属性
                this.aiDifficulty = 'medium';
                this.aiThinkingTime = 500;
                this.aiLastMoveTime = 0;
                this.aiMoves = [];
                
                // 绑定键盘事件（仅非AI）
                if (!this.isAI) {
                    this.setupControls();
                }
            }
            
            // 设置控制
            setupControls() {
                document.addEventListener('keydown', (e) => {
                    if (this.gameOver || !this.currentPiece) return;
                    
                    switch(e.key) {
                        case 'ArrowLeft':
                            this.movePiece(-1, 0);
                            break;
                        case 'ArrowRight':
                            this.movePiece(1, 0);
                            break;
                        case 'ArrowDown':
                            this.movePiece(0, 1);
                            break;
                        case 'ArrowUp':
                            this.rotatePiece();
                            break;
                        case ' ':
                            this.hardDrop();
                            break;
                    }
                });
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
            
            // 检查碰撞
            collision(offsetX = 0, offsetY = 0, piece = this.currentPiece) {
                if (!piece) return false;
                
                for (let y = 0; y < piece.shape.length; y++) {
                    for (let x = 0; x < piece.shape[y].length; x++) {
                        if (piece.shape[y][x] !== 0) {
                            const newX = piece.x + x + offsetX;
                            const newY = piece.y + y + offsetY;
                            
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
            
            // 移动方块
            movePiece(dirX, dirY) {
                if (!this.collision(dirX, dirY)) {
                    this.currentPiece.x += dirX;
                    this.currentPiece.y += dirY;
                    return true;
                }
                
                // 如果是向下移动且发生碰撞，则固定方块
                if (dirY > 0) {
                    this.lockPiece();
                    this.clearLines();
                    this.spawnPiece();
                }
                
                return false;
            }
            
            // 旋转方块
            rotatePiece() {
                const rotated = this.currentPiece.rotate();
                const previousShape = this.currentPiece.shape;
                this.currentPiece.shape = rotated;
                
                // 碰撞检测与墙踢
                if (this.collision()) {
                    // 尝试向左墙踢
                    if (!this.collision(-1, 0)) {
                        this.currentPiece.x--;
                    } 
                    // 尝试向右墙踢
                    else if (!this.collision(1, 0)) {
                        this.currentPiece.x++;
                    }
                    // 尝试向下墙踢
                    else if (!this.collision(0, 1)) {
                        this.currentPiece.y++;
                    }
                    // 如果所有墙踢都失败，恢复原始形状
                    else {
                        this.currentPiece.shape = previousShape;
                    }
                }
            }
            
            // 硬降落
            hardDrop() {
                while (this.movePiece(0, 1)) {
                    this.score += 2;
                }
            }
            
            // 固定方块
            lockPiece() {
                for (let y = 0; y < this.currentPiece.shape.length; y++) {
                    for (let x = 0; x < this.currentPiece.shape[y].length; x++) {
                        if (this.currentPiece.shape[y][x] !== 0) {
                            const boardY = this.currentPiece.y + y;
                            const boardX = this.currentPiece.x + x;
                            
                            if (boardY >= 0) {
                                this.grid[boardY][boardX] = this.currentPiece.color;
                            }
                        }
                    }
                }
                
                this.currentPiece = null;
            }
            
            // 清除完整的行
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
                    // 计算分数
                    const linePoints = [0, 40, 100, 300, 1200];
                    this.score += linePoints[linesCleared] * this.level;
                    this.lines += linesCleared;
                    
                    // 更新等级
                    this.level = Math.floor(this.lines / 10) + 1;
                    this.dropInterval = Math.max(100, 1000 - (this.level - 1) * 100);
                }
            }
            
            // AI移动决策
            makeAIMove() {
                if (!this.currentPiece || this.gameOver) return;
                
                const now = Date.now();
                if (now - this.aiLastMoveTime < this.aiThinkingTime) return;
                
                // 根据难度设置AI思考时间
                const difficultySettings = {
                    easy: { thinkingTime: 800, randomness: 0.3 },
                    medium: { thinkingTime: 500, randomness: 0.1 },
                    hard: { thinkingTime: 200, randomness: 0.05 }
                };
                
                const settings = difficultySettings[this.aiDifficulty];
                this.aiThinkingTime = settings.thinkingTime;
                
                // 获取所有可能的移动
                const possibleMoves = this.getAllPossibleMoves();
                
                // 评估每个移动
                let bestMove = null;
                let bestScore = -Infinity;
                
                for (const move of possibleMoves) {
                    const score = this.evaluateMove(move);
                    
                    // 添加随机性
                    if (Math.random() < settings.randomness) {
                        score += Math.random() * 100 - 50;
                    }
                    
                    if (score > bestScore) {
                        bestScore = score;
                        bestMove = move;
                    }
                }
                
                // 执行最佳移动
                if (bestMove) {
                    this.executeMove(bestMove);
                    this.aiLastMoveTime = now;
                }
            }
            
            // 获取所有可能的移动
            getAllPossibleMoves() {
                const moves = [];
                const originalPiece = {
                    shape: this.currentPiece.shape.map(row => [...row]),
                    x: this.currentPiece.x,
                    y: this.currentPiece.y
                };
                
                // 旋转状态
                const rotations = [0, 1, 2, 3]; // 0-3次旋转
                
                for (const rotation of rotations) {
                    // 重置方块
                    this.currentPiece.shape = originalPiece.shape.map(row => [...row]);
                    this.currentPiece.x = originalPiece.x;
                    this.currentPiece.y = originalPiece.y;
                    
                    // 应用旋转
                    for (let i = 0; i < rotation; i++) {
                        this.currentPiece.shape = this.currentPiece.rotate();
                    }
                    
                    // 水平位置
                    for (let x = -COLS; x < COLS * 2; x++) {
                        if (!this.collision(x, 0)) {
                            // 下落位置
                            let dropY = 0;
                            while (!this.collision(x, dropY + 1)) {
                                dropY++;
                            }
                            
                            moves.push({
                                rotation,
                                x: originalPiece.x + x,
                                y: originalPiece.y + dropY,
                                dropY
                            });
                        }
                    }
                }
                
                // 恢复原始方块
                this.currentPiece.shape = originalPiece.shape.map(row => [...row]);
                this.currentPiece.x = originalPiece.x;
                this.currentPiece.y = originalPiece.y;
                
                return moves;
            }
            
            // 评估移动
            evaluateMove(move) {
                // 临时应用移动
                const originalPiece = {
                    shape: this.currentPiece.shape.map(row => [...row]),
                    x: this.currentPiece.x,
                    y: this.currentPiece.y
                };
                
                // 应用旋转
                for (let i = 0; i < move.rotation; i++) {
                    this.currentPiece.shape = this.currentPiece.rotate();
                }
                
                // 应用位置
                this.currentPiece.x = move.x;
                this.currentPiece.y = move.y;
                
                // 评估分数
                let score = 0;
                
                // 1. 高度评估（越低越好）
                const height = this.getMaxHeight();
                score -= height * 10;
                
                // 2. 凹洞评估（越少越好）
                const holes = this.countHoles();
                score -= holes * 50;
                
                // 3. 平整度评估（越平整越好）
                const bumpiness = this.getBumpiness();
                score -= bumpiness * 2;
                
                // 4. 行清除评估（越多越好）
                const clearedLines = this.simulateClearLines();
                score += clearedLines * 1000;
                
                // 5. 接近顶部评估