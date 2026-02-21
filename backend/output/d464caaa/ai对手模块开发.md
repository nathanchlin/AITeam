# AI对手模块开发

**Agent**: coder

**Time**: 2026-02-19T15:27:17.426984

---

我将为您开发一个完整的俄罗斯方块对战游戏，包含AI对手模块。这个游戏将具有不同难度的AI对手，实现完整的游戏逻辑和反应机制。

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
            gap: 30px;
            background-color: #0f0f1e;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 0 30px rgba(0, 0, 0, 0.5);
        }
        
        .game-area {
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        
        canvas {
            border: 2px solid #16213e;
            background-color: #0f3460;
            box-shadow: 0 0 15px rgba(0, 0, 0, 0.3);
        }
        
        .info-panel {
            margin-top: 15px;
            text-align: center;
        }
        
        .score {
            font-size: 18px;
            margin-bottom: 10px;
        }
        
        .controls {
            margin-top: 20px;
            text-align: center;
            width: 100%;
        }
        
        .controls h3 {
            margin-bottom: 10px;
            color: #e94560;
        }
        
        .difficulty-selector {
            margin-bottom: 20px;
            text-align: center;
        }
        
        .difficulty-selector label {
            margin-right: 15px;
            cursor: pointer;
        }
        
        .difficulty-selector input[type="radio"] {
            margin-right: 5px;
        }
        
        button {
            background-color: #e94560;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            transition: background-color 0.3s;
            margin: 5px;
        }
        
        button:hover {
            background-color: #c13651;
        }
        
        .game-over {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background-color: rgba(15, 15, 30, 0.9);
            padding: 30px;
            border-radius: 10px;
            text-align: center;
            display: none;
        }
        
        .game-over h2 {
            color: #e94560;
            margin-bottom: 20px;
        }
        
        .next-piece {
            margin-top: 10px;
            text-align: center;
        }
        
        .next-piece canvas {
            border: 1px solid #16213e;
            background-color: #0f3460;
        }
    </style>
</head>
<body>
    <div class="game-container">
        <div class="game-area">
            <canvas id="player-canvas" width="300" height="600"></canvas>
            <div class="info-panel">
                <div class="score">分数: <span id="player-score">0</span></div>
                <div class="score">等级: <span id="player-level">1</span></div>
                <div class="score">消除行数: <span id="player-lines">0</span></div>
                <div class="next-piece">
                    <div>下一个方块:</div>
                    <canvas id="player-next" width="100" height="80"></canvas>
                </div>
            </div>
        </div>
        
        <div class="game-area">
            <canvas id="ai-canvas" width="300" height="600"></canvas>
            <div class="info-panel">
                <div class="score">分数: <span id="ai-score">0</span></div>
                <div class="score">等级: <span id="ai-level">1</span></div>
                <div class="score">消除行数: <span id="ai-lines">0</span></div>
                <div class="next-piece">
                    <div>下一个方块:</div>
                    <canvas id="ai-next" width="100" height="80"></canvas>
                </div>
            </div>
        </div>
    </div>
    
    <div class="controls">
        <div class="difficulty-selector">
            <label><input type="radio" name="difficulty" value="easy" checked> 简单</label>
            <label><input type="radio" name="difficulty" value="medium"> 中等</label>
            <label><input type="radio" name="difficulty" value="hard"> 困难</label>
            <label><input type="radio" name="difficulty" value="expert"> 专家</label>
        </div>
        <button id="start-btn">开始游戏</button>
        <button id="pause-btn">暂停</button>
        <h3>操作说明:</h3>
        <p>← → : 左右移动 | ↓ : 加速下落 | ↑ : 旋转 | 空格 : 直接落下</p>
    </div>
    
    <div class="game-over" id="game-over">
        <h2 id="game-over-message">游戏结束!</h2>
        <p id="final-scores"></p>
        <button id="restart-btn">重新开始</button>
    </div>

    <script>
        // 游戏常量
        const COLS = 10;
        const ROWS = 20;
        const BLOCK_SIZE = 30;
        
        // 方块形状定义
        const SHAPES = [
            // I
            [
                [0, 0, 0, 0],
                [1, 1, 1, 1],
                [0, 0, 0, 0],
                [0, 0, 0, 0]
            ],
            // J
            [
                [1, 0, 0],
                [1, 1, 1],
                [0, 0, 0]
            ],
            // L
            [
                [0, 0, 1],
                [1, 1, 1],
                [0, 0, 0]
            ],
            // O
            [
                [1, 1],
                [1, 1]
            ],
            // S
            [
                [0, 1, 1],
                [1, 1, 0],
                [0, 0, 0]
            ],
            // T
            [
                [0, 1, 0],
                [1, 1, 1],
                [0, 0, 0]
            ],
            // Z
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
            constructor(canvas, nextCanvas, isAI = false) {
                this.canvas = canvas;
                this.ctx = canvas.getContext('2d');
                this.nextCanvas = nextCanvas;
                this.nextCtx = nextCanvas.getContext('2d');
                this.isAI = isAI;
                
                this.board = Array(ROWS).fill().map(() => Array(COLS).fill(0));
                this.score = 0;
                this.level = 1;
                this.lines = 0;
                this.gameOver = false;
                this.paused = false;
                
                this.currentPiece = null;
                this.nextPiece = null;
                this.dropCounter = 0;
                this.dropInterval = 1000;
                this.lastTime = 0;
                
                this.aiDifficulty = 'easy';
                this.aiThinkingTime = 0;
                this.aiBestMove = null;
                
                this.generateNewPiece();
            }
            
            // 生成新方块
            generateNewPiece() {
                if (this.nextPiece) {
                    this.currentPiece = this.nextPiece;
                } else {
                    const typeId = Math.floor(Math.random() * SHAPES.length);
                    this.currentPiece = {
                        shape: SHAPES[typeId],
                        color: COLORS[typeId],
                        x: Math.floor(COLS / 2) - Math.floor(SHAPES[typeId][0].length / 2),
                        y: 0,
                        typeId: typeId
                    };
                }
                
                const typeId = Math.floor(Math.random() * SHAPES.length);
                this.nextPiece = {
                    shape: SHAPES[typeId],
                    color: COLORS[typeId],
                    x: 0,
                    y: 0,
                    typeId: typeId
                };
                
                // 检查游戏是否结束
                if (this.collision()) {
                    this.gameOver = true;
                }
            }
            
            // 碰撞检测
            collision() {
                for (let y = 0; y < this.currentPiece.shape.length; y++) {
                    for (let x = 0; x < this.currentPiece.shape[y].length; x++) {
                        if (this.currentPiece.shape[y][x] !== 0) {
                            const boardX = this.currentPiece.x + x;
                            const boardY = this.currentPiece.y + y;
                            
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
            
            // 合并方块到游戏板
            merge() {
                for (let y = 0; y < this.currentPiece.shape.length; y++) {
                    for (let x = 0; x < this.currentPiece.shape[y].length; x++) {
                        if (this.currentPiece.shape[y][x] !== 0) {
                            const boardY = this.currentPiece.y + y;
                            const boardX = this.currentPiece.x + x;
                            
                            if (boardY >= 0) {
                                this.board[boardY][boardX] = this.currentPiece.typeId + 1;
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
                        y++; // 重新检查当前行
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
                }
            }
            
            // 旋转方块
            rotate() {
                const rotated = [];
                const shape = this.currentPiece.shape;
                
                for (let x = 0; x < shape[0].length; x++) {
                    rotated.push([]);
                    for (let y = shape.length - 1; y >= 0; y--) {
                        rotated[x].push(shape[y][x]);
                    }
                }
                
                const previousShape = this.currentPiece.shape;
                this.currentPiece.shape = rotated;
                
                if (this.collision()) {
                    this.currentPiece.shape = previousShape;
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
            
            // 硬降
            hardDrop() {
                while (this.move(1)) {
                    this.score += 2;
                }
                this.drop();
            }
            
            // 软降
            softDrop() {
                if (this.move(1)) {
                    this.score += 1;
                    return true;
                }
                return false;
            }
            
            // 方块下落
            drop() {
                this.currentPiece.y++;
                
                if (this.collision()) {
                    this.currentPiece.y--;
                    this.merge();
                    this.clearLines();
                    this.generateNewPiece();
                }
            }
            
            // 更新游戏状态
            update(time = 0) {
                if (this.gameOver || this.paused) return;
                
                const deltaTime = time - this.lastTime;
                this.lastTime = time;
                
                this.dropCounter += deltaTime;
                if (this.dropCounter > this.dropInterval) {
                    this.drop();
                    this.dropCounter = 0;
                }
                
                // AI决策
                if (this.isAI && this.currentPiece && !this.aiBestMove) {
                    this.aiThinkingTime += deltaTime;
                    
                    // 根据难度设置AI思考时间
                    const thinkTime = {
                        'easy': 500,
                        'medium': 300,
                        'hard': 200,
                        'expert': 100
                    }[this.aiDifficulty];
                    
                    if (this.aiThinkingTime >= thinkTime) {
                        this.aiBestMove = this.calculateBestMove();
                        this.aiThinkingTime = 0;
                    }
                }
                
                // 执行AI最佳移动
                if (this.isAI && this.aiBestMove && this.currentPiece) {
                    if (this.aiBestMove.moves.length > 0) {
                        const move = this.aiBestMove.moves.shift();
                        
                        if (move === 'rotate') {
                            this.rotate();
                        } else if (move === 'left') {
                            this.move(-1);
                        } else if (move === 'right') {
                            this.move(1);
                        } else if (move === 'drop') {
                            this.drop();
                        }
                    } else {
                        this.aiBestMove = null;
                    }
                }
            }
            
            // AI计算最佳移动
            calculateBestMove() {
                const moves = [];
                const possibleMoves = [];
                
                // 生成所有可能的移动
                const rotations = [0, 1, 2, 3]; // 最多旋转4次
                const positions = Array(COLS).fill(0).map((_, i) => i - 3); // 向左最多移动3格
                
                // 保存当前状态
                const originalPiece = {
                    shape: this.currentPiece.shape.map(row => [...row]),
                    x: this.currentPiece.x,
                    y: this.currentPiece.y,
                    typeId: this.currentPiece.typeId
                };
                
                // 尝试所有可能的旋转和位置
                for (const rotation of rotations) {
                    // 旋转方块
                    if (rotation > 0) {
                        this.rotate();
                    }
                    
                    // 尝试所有位置
                    for (const pos of positions) {
                        // 保存当前状态
                        const originalX = this.currentPiece.x;
                        
                        // 水平移动
                        this.currentPiece.x = originalX + pos;
                        
                        // 检查是否碰撞
                        if (!this.collision()) {
                            // 计算最终位置
                            let finalY = this.currentPiece.y;
                            while (!this.collision()) {
                                this.currentPiece.y++;
                                finalY++;
                            }
                            this.currentPiece.y--;
                            
                            // 评估这个位置
                            const evaluation = this.evaluatePosition();
                            
                            // 保存移动序列
                            const moveSequence = [];
                            
                            // 添加旋转移动
                            for (let i = 0; i < rotation; i++) {
                                moveSequence.push('rotate');
                            }
                            
                            // 添加水平移动
                            if (pos > 0) {
                                for (let i = 0; i < pos; i++) {
                                    moveSequence.push('right');
                                }
                            } else if (pos < 0) {
                                for (let i = 0; i < -pos; i++) {
                                    moveSequence.push('left');
                                }
                            }
                            
                            // 添加下落移动
                            const dropDistance = finalY - this.currentPiece.y;
                            for (let i = 0; i < dropDistance; i++) {
                                moveSequence.push('drop');
                            }
                            
                            possibleMoves.push({
                                moves: [...moveSequence],
                                evaluation: evaluation
                            });
                        }
                        
                        // 恢复位置
                        this.currentPiece.x = originalX;
                    }
                    
                    // 恢复旋转
                    if (rotation > 0) {
                        this.rotate();
                        this.rotate();
                        this.rotate();
                    }
                }
                
                // 恢复原始状态
                this.currentPiece = originalPiece;
                
                // 根据难度选择最佳移动
                if (possibleMoves.length === 0) {
                    return { moves: ['drop'], evaluation: -1000 };
                }
                
                // 排序可能的移动
                possibleMoves.sort((a, b) => b.evaluation - a.evaluation);
                
                // 根据难度选择移动
                const difficulty = this.aiDifficulty;
                let selectedMove;
                
                if (difficulty === 'easy') {
                    // 简单：随机选择前50%的移动
                    const topHalf = Math.ceil(possibleMoves.length / 2);
                    selectedMove = possibleMoves[Math.floor(Math.random() * topHalf)];
                } else if (difficulty === 'medium') {
                    // 中等：随机选择前30%的移动
                    const topThird = Math.ceil(possibleMoves.length * 0.3);
                    selectedMove = possibleMoves[Math.floor(Math.random() * topThird)];
                } else if (difficulty === 'hard') {
                    // 困