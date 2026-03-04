# 双人分屏游戏界面与Canvas渲染

**Time**: 2026-02-28T15:11:04.067529

---

我来完成这个双人分屏俄罗斯方块对战游戏的实现。需要完善Canvas渲染、霓虹发光效果、3个预览方块显示、Hold区域、以及完整的游戏逻辑。

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tetris Battle - 俄罗斯方块对战</title>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #0a0a0f;
            --bg-secondary: #12121a;
            --fg: #e8e8e8;
            --muted: #6b6b7b;
            --accent: #00f5d4;
            --accent-glow: rgba(0, 245, 212, 0.3);
            --border: #2a2a3a;
            --card: #16161f;
            --grid-line: #1a1a25;
            --danger: #ff006e;
            --warning: #ff9500;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'JetBrains Mono', monospace;
            background: var(--bg);
            color: var(--fg);
            min-height: 100vh;
            overflow-x: hidden;
            position: relative;
        }

        .bg-layer {
            position: fixed;
            inset: 0;
            z-index: 0;
            pointer-events: none;
        }

        .bg-gradient {
            background: 
                radial-gradient(ellipse at 20% 20%, rgba(0, 245, 212, 0.1) 0%, transparent 50%),
                radial-gradient(ellipse at 80% 80%, rgba(255, 0, 110, 0.1) 0%, transparent 50%),
                radial-gradient(ellipse at 50% 50%, rgba(58, 134, 255, 0.08) 0%, transparent 60%);
            filter: blur(60px);
        }

        .grid-pattern {
            background-image: 
                linear-gradient(var(--grid-line) 1px, transparent 1px),
                linear-gradient(90deg, var(--grid-line) 1px, transparent 1px);
            background-size: 40px 40px;
            opacity: 0.4;
        }

        .game-container {
            position: relative;
            z-index: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 15px;
            min-height: 100vh;
        }

        .header {
            text-align: center;
            margin-bottom: 15px;
        }

        .title {
            font-family: 'Orbitron', sans-serif;
            font-size: clamp(1.5rem, 4vw, 2.2rem);
            font-weight: 900;
            letter-spacing: 0.15em;
            color: var(--fg);
            text-transform: uppercase;
            text-shadow: 0 0 30px rgba(0, 245, 212, 0.3);
        }

        .subtitle {
            font-size: 0.75rem;
            color: var(--muted);
            margin-top: 6px;
            letter-spacing: 0.25em;
        }

        .battle-arena {
            display: flex;
            gap: 30px;
            align-items: flex-start;
            flex-wrap: nowrap;
            justify-content: center;
        }

        @media (max-width: 900px) {
            .battle-arena {
                flex-wrap: wrap;
                gap: 20px;
            }
        }

        .player-section {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 12px;
        }

        .player-label {
            font-family: 'Orbitron', sans-serif;
            font-size: 0.85rem;
            font-weight: 700;
            letter-spacing: 0.15em;
            padding: 6px 16px;
            border: 1px solid var(--border);
            background: var(--card);
            border-radius: 4px;
        }

        .player-label.p1 {
            color: var(--accent);
            border-color: var(--accent);
            box-shadow: 0 0 20px var(--accent-glow), inset 0 0 20px rgba(0, 245, 212, 0.1);
        }

        .player-label.p2 {
            color: var(--danger);
            border-color: var(--danger);
            box-shadow: 0 0 20px rgba(255, 0, 110, 0.3), inset 0 0 20px rgba(255, 0, 110, 0.1);
        }

        .game-board {
            display: flex;
            gap: 10px;
            padding: 12px;
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 8px;
            box-shadow: 
                0 4px 40px rgba(0, 0, 0, 0.5),
                inset 0 1px 0 rgba(255, 255, 255, 0.03);
        }

        .side-panel {
            display: flex;
            flex-direction: column;
            gap: 10px;
            width: 90px;
        }

        .panel-box {
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 10px 8px;
        }

        .panel-title {
            font-family: 'Orbitron', sans-serif;
            font-size: 0.6rem;
            font-weight: 700;
            color: var(--muted);
            letter-spacing: 0.12em;
            margin-bottom: 8px;
            text-align: center;
            text-transform: uppercase;
        }

        .preview-canvas {
            display: block;
            margin: 0 auto;
        }

        .stats {
            display: flex;
            flex-direction: column;
            gap: 6px;
        }

        .stat-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 2px;
        }

        .stat-label {
            font-size: 0.55rem;
            color: var(--muted);
            letter-spacing: 0.1em;
            text-transform: uppercase;
        }

        .stat-value {
            font-family: 'Orbitron', sans-serif;
            font-size: 1rem;
            font-weight: 700;
            color: var(--fg);
        }

        .stat-value.score {
            color: var(--warning);
            text-shadow: 0 0 10px rgba(255, 149, 0, 0.5);
        }

        .stat-value.level {
            color: var(--accent);
            text-shadow: 0 0 10px var(--accent-glow);
        }

        .stat-value.lines {
            color: var(--danger);
            text-shadow: 0 0 10px rgba(255, 0, 110, 0.5);
        }

        .main-canvas {
            border-radius: 4px;
            box-shadow: inset 0 0 30px rgba(0, 0, 0, 0.5);
        }

        .controls-hint {
            margin-top: 20px;
            display: flex;
            gap: 40px;
            flex-wrap: wrap;
            justify-content: center;
        }

        .control-group {
            text-align: center;
        }

        .control-title {
            font-family: 'Orbitron', sans-serif;
            font-size: 0.7rem;
            font-weight: 700;
            margin-bottom: 8px;
            letter-spacing: 0.1em;
        }

        .control-title.p1 { color: var(--accent); }
        .control-title.p2 { color: var(--danger); }

        .control-keys {
            font-size: 0.65rem;
            color: var(--muted);
            line-height: 1.6;
        }

        .key {
            display: inline-block;
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 3px;
            padding: 2px 6px;
            margin: 1px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.6rem;
        }

        .game-status {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(10, 10, 15, 0.95);
            border: 2px solid var(--accent);
            border-radius: 12px;
            padding: 30px 50px;
            text-align: center;
            z-index: 100;
            display: none;
            box-shadow: 0 0 60px rgba(0, 245, 212, 0.3);
        }

        .game-status.show {
            display: block;
            animation: fadeIn 0.3s ease-out;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translate(-50%, -50%) scale(0.9); }
            to { opacity: 1; transform: translate(-50%, -50%) scale(1); }
        }

        .status-title {
            font-family: 'Orbitron', sans-serif;
            font-size: 1.5rem;
            font-weight: 900;
            margin-bottom: 15px;
            letter-spacing: 0.1em;
        }

        .status-title.p1-win { color: var(--accent); }
        .status-title.p2-win { color: var(--danger); }

        .restart-btn {
            font-family: 'Orbitron', sans-serif;
            font-size: 0.8rem;
            font-weight: 700;
            padding: 12px 30px;
            background: transparent;
            border: 2px solid var(--accent);
            color: var(--accent);
            border-radius: 6px;
            cursor: pointer;
            letter-spacing: 0.1em;
            transition: all 0.2s ease;
            margin-top: 10px;
        }

        .restart-btn:hover {
            background: var(--accent);
            color: var(--bg);
            box-shadow: 0 0 30px var(--accent-glow);
        }

        .center-panel {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 0 15px;
        }

        .vs-divider {
            font-family: 'Orbitron', sans-serif;
            font-size: 1.8rem;
            font-weight: 900;
            color: var(--muted);
            letter-spacing: 0.2em;
            text-shadow: 0 0 20px rgba(255, 255, 255, 0.1);
        }
    </style>
</head>
<body>
    <div class="bg-layer bg-gradient"></div>
    <div class="bg-layer grid-pattern"></div>

    <div class="game-container">
        <header class="header">
            <h1 class="title">Tetris Battle</h1>
            <p class="subtitle">PRESS START TO BEGIN</p>
        </header>

        <div class="battle-arena">
            <!-- Player 1 -->
            <div class="player-section">
                <div class="player-label p1">PLAYER 1</div>
                <div class="game-board">
                    <div class="side-panel">
                        <div class="panel-box">
                            <div class="panel-title">Hold</div>
                            <canvas id="hold1" class="preview-canvas" width="70" height="50"></canvas>
                        </div>
                        <div class="panel-box">
                            <div class="stats">
                                <div class="stat-item">
                                    <span class="stat-label">Score</span>
                                    <span class="stat-value score" id="score1">0</span>
                                </div>
                                <div class="stat-item">
                                    <span class="stat-label">Level</span>
                                    <span class="stat-value level" id="level1">1</span>
                                </div>
                                <div class="stat-item">
                                    <span class="stat-label">Lines</span>
                                    <span class="stat-value lines" id="lines1">0</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    <canvas id="board1" class="main-canvas" width="200" height="400"></canvas>
                    <div class="side-panel">
                        <div class="panel-box">
                            <div class="panel-title">Next</div>
                            <canvas id="next1" class="preview-canvas" width="70" height="170"></canvas>
                        </div>
                    </div>
                </div>
            </div>

            <!-- VS Divider -->
            <div class="center-panel">
                <div class="vs-divider">VS</div>
            </div>

            <!-- Player 2 -->
            <div class="player-section">
                <div class="player-label p2">PLAYER 2</div>
                <div class="game-board">
                    <div class="side-panel">
                        <div class="panel-box">
                            <div class="panel-title">Hold</div>
                            <canvas id="hold2" class="preview-canvas" width="70" height="50"></canvas>
                        </div>
                        <div class="panel-box">
                            <div class="stats">
                                <div class="stat-item">
                                    <span class="stat-label">Score</span>
                                    <span class="stat-value score" id="score2">0</span>
                                </div>
                                <div class="stat-item">
                                    <span class="stat-label">Level</span>
                                    <span class="stat-value level" id="level2">1</span>
                                </div>
                                <div class="stat-item">
                                    <span class="stat-label">Lines</span>
                                    <span class="stat-value lines" id="lines2">0</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    <canvas id="board2" class="main-canvas" width="200" height="400"></canvas>
                    <div class="side-panel">
                        <div class="panel-box">
                            <div class="panel-title">Next</div>
                            <canvas id="next2" class="preview-canvas" width="70" height="170"></canvas>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="controls-hint">
            <div class="control-group">
                <div class="control-title p1">Player 1</div>
                <div class="control-keys">
                    <span class="key">W</span> Rotate
                    <span class="key">A</span><span class="key">S</span><span class="key">D</span> Move<br>
                    <span class="key">Space</span> Hard Drop
                    <span class="key">Q</span> Hold
                </div>
            </div>
            <div class="control-group">
                <div class="control-title p2">Player 2</div>
                <div class="control-keys">
                    <span class="key">↑</span> Rotate
                    <span class="key">←</span><span class="key">↓</span><span class="key">→</span> Move<br>
                    <span class="key">Enter</span> Hard Drop
                    <span class="key">Shift</span> Hold
                </div>
            </div>
        </div>
    </div>

    <div class="game-status" id="gameStatus">
        <div class="status-title" id="statusTitle">GAME OVER</div>
        <button class="restart-btn" id="restartBtn">RESTART</button>
    </div>

    <script>
        // ============================================
        // TETRIS BATTLE - 完整双人对战版
        // ============================================

        const COLS = 10;
        const ROWS = 20;
        const BLOCK_SIZE = 20;
        const EMPTY = 0;
        const PREVIEW_COUNT = 3;

        // 霓虹风格配色 - 高对比度
        const COLORS = {
            I: { main: '#00f5d4', glow: 'rgba(0, 245, 212, 0.6)', dark: '#00a896' },
            O: { main: '#fee440', glow: 'rgba(254, 228, 64, 0.6)', dark: '#c9b318' },
            T: { main: '#f15bb5', glow: 'rgba(241, 91, 181, 0.6)', dark: '#b5478a' },
            S: { main: '#00bb7c', glow: 'rgba(0, 187, 124, 0.6)', dark: '#008a5c' },
            Z: { main: '#ff006e', glow: 'rgba(255, 0, 110, 0.6)', dark: '#cc0058' },
            J: { main: '#3a86ff', glow: 'rgba(58, 134, 255, 0.6)', dark: '#2c68cc' },
            L: { main: '#ff9500', glow: 'rgba(255, 149, 0, 0.6)', dark: '#cc7700' },
            ghost: 'rgba(255, 255, 255, 0.12)',
            grid: '#14141c',
            gridLine: '#1e1e2a'
        };

        // SRS标准方块形状
        const TETROMINOES = {
            I: {
                shape: [
                    [[0,0,0,0], [1,1,1,1], [0,0,0,0], [0,0,0,0]],
                    [[0,0,1,0], [0,0,1,0], [0,0,1,0], [0,0,1,0]],
                    [[0,0,0,0], [0,0,0,0], [1,1,1,1], [0,0,0,0]],
                    [[0,1,0,0], [0,1,0,0], [0,1,0,0], [0,1,0,0]]
                ],
                color: COLORS.I
            },
            O: {
                shape: [[[1,1], [1,1]], [[1,1], [1,1]], [[1,1], [1,1]], [[1,1], [1,1]]],
                color: COLORS.O
            },
            T: {
                shape: [
                    [[0,1,0], [1,1,1], [0,0,0]],
                    [[0,1,0], [0,1,1], [0,1,0]],
                    [[0,0,0], [1,1,1], [0,1,0]],
                    [[0,1,0], [1,1,0], [0,1,0]]
                ],
                color: COLORS.T
            },
            S: {
                shape: [
                    [[0,1,1], [1,1,0], [0,0,0]],
                    [[0,1,0], [0,1,1], [0,0,1]],
                    [[0,0,0], [0,1,1], [1,1,0]],
                    [[1,0,0], [1,1,0], [0,1,0]]
                ],
                color: COLORS.S
            },
            Z: {
                shape: [
                    [[1,1,0], [0,1,1], [0,0,0]],
                    [[0,0,1], [0,1,1], [0,1,0]],
                    [[0,0,0], [1,1,0], [0,1,1]],
                    [[0,1,0], [1,1,0], [1,0,0]]
                ],
                color: COLORS.Z
            },
            J: {
                shape: [
                    [[1,0,0], [1,1,1], [0,0,0]],
                    [[0,1,1], [0,1,0], [0,1,0]],
                    [[0,0,0], [1,1,1], [0,0,1]],
                    [[0,1,0], [0,1,0], [1,1,0]]
                ],
                color: COLORS.J
            },
            L: {
                shape: [
                    [[0,0,1], [1,1,1], [0,0,0]],
                    [[0,1,0], [0,1,0], [0,1,1]],
                    [[0,0,0], [1,1,1], [1,0,0]],
                    [[1,1,0], [0,1,0], [0,1,0]]
                ],
                color: COLORS.L
            }
        };

        // SRS踢墙数据
        const SRS_KICKS = {
            JLSTZ: {
                '0>1': [[0,0],[-1,0],[-1,1],[0,-2],[-1,-2]],
                '1>0': [[0,0],[1,0],[1,-1],[0,2],[1,2]],
                '1>2': [[0,0],[1,0],[1,-1],[0,2],[1,2]],
                '2>1': [[0,0],[-1,0],[-1,1],[0,-2],[-1,-2]],
                '2>3': [[0,0],[1,0],[1,1],[0,-2],[1,-2]],
                '3>2': [[0,0],[-1,0],[-1,-1],[0,2],[-1,2]],
                '3>0': [[0,0],[-1,0],[-1,-1],[0,2],[-1,2]],
                '0>3': [[0,0],[1,0],[1,1],[0,-2],[1,-2]]
            },
            I: {
                '0>1': [[0,0],[-2,0],[1,0],[-2,-1],[1,2]],
                '1>0': [[0,0],[2,0],[-1,0],[2,1],[-1,-2]],
                '1>2': [[0,0],[-1,0],[2,0],[-1,2],[2,-1]],
                '2>1': [[0,0],[1,0],[-2,0],[1,-2],[-2,1]],
                '2>3': [[0,0],[2,0],[-1,0],[2,1],[-1,-2]],
                '3>2': [[0,0],[-2,0],[1,0],[-2,-1],[1,2]],
                '3>0': [[0,0],[1,0],[-2,0],[1,-2],[-2,1]],
                '0>3': [[0,0],[-1,0],[2,0],[-1,2],[2,-1]]
            }
        };

        // ============================================
        // 方块类
        // ============================================
        class Tetromino {
            constructor(type) {
                this.type = type;
                this.shape = TETROMINOES[type].shape;
                this.color = TETROMINOES[type].color;
                this.rotation = 0;
                this.x = Math.floor(COLS / 2) - Math.floor(this.shape[0][0].length / 2);
                this.y = 0;
            }

            getCurrentShape() {
                return this.shape[this.rotation];
            }

            rotate(dir = 1) {
                const old = this.rotation;
                this.rotation = dir === 1 ? (this.rotation + 1) % 4 : (this.rotation + 3) % 4;
                return old;
            }
        }

        // ============================================
        // 游戏主类
        // ============================================
        class TetrisGame {
            constructor(boardId, nextId, holdId, scoreId, levelId, linesId, playerNum) {
                this.canvas = document.getElementById(boardId);
                this.ctx = this.canvas.getContext('2d');
                this.nextCanvas = document.getElementById(nextId);
                this.nextCtx = this.nextCanvas.getContext('2d');
                this.holdCanvas = document.getElementById(holdId);
                this.holdCtx = this.holdCanvas.getContext('2d');

                this.scoreEl = document.getElementById(scoreId);
                this.levelEl = document.getElementById(levelId);
                this.linesEl = document.getElementById(linesId);

                this.playerNum = playerNum;

                // 初始化所有状态
                this.board = this.createBoard();
                this.score = 0;
                this.level = 1;
                this.lines = 0;
                this.currentPiece = null;
                this.nextPieces = [];
                this.holdPiece = null;
                this.canHold = true;
                this.gameOver = false;
                this.lastDrop = 0;
                this.dropInterval = 800;
                this.bag = [];

                // 预生成3个方块
                for (let i = 0; i < PREVIEW_COUNT; i++) {
                    this.nextPieces.push(this.getNextFromBag());
                }

                this.spawnPiece();
                this.updateStats();
                this.draw();
            }

            createBoard() {
                return Array.from({ length: ROWS }, () => Array(COLS).fill(EMPTY));
            }

            getNextFromBag() {
                if (this.bag.length === 0) {
                    this.bag = ['I', 'O', 'T', 'S', 'Z', 'J', 'L'];
                    for (let i = this.bag.length - 1; i > 0; i--) {
                        const j = Math.floor(Math.random() * (i + 1));
                        [this.bag[i], this.bag[j]] = [this.bag[j], this.bag[i]];
                    }
                }
                return new Tetromino(this.bag.pop());
            }

            spawnPiece() {
                this.currentPiece = this.nextPieces.shift();
                this.nextPieces.push(this.getNextFromBag());
                this.canHold = true;

                this.currentPiece.x = Math.floor(COLS / 2) - Math.floor(this.currentPiece.getCurrentShape()[0].length / 2);
                this.currentPiece.y = 0;

                if (this.checkCollision(this.currentPiece, 0, 0)) {
                    this.gameOver = true;
                }

                this.drawNext();
                this.drawHold();
            }

            checkCollision(piece, ox, oy, shape = null) {
                const s = shape || piece.getCurrentShape();
                for (let y = 0; y < s.length; y++) {
                    for (let x = 0; x < s[y].length; x++) {
                        if (s[y][x]) {
                            const nx = piece.x + x + ox;
                            const ny = piece.y + y + oy;
                            if (nx < 0 || nx >= COLS || ny >= ROWS) return true;
                            if (ny >= 0 && this.board[ny][nx] !== EMPTY) return true;
                        }
                    }
                }
                return false;
            }

            rotatePiece(dir = 1) {
                if (!this.currentPiece || this.currentPiece.type === 'O') return false;

                const oldRot = this.currentPiece.rotation;
                this.currentPiece.rotate(dir);
                const newRot = this.currentPiece.rotation;

                const kicks = this.currentPiece.type === 'I' ? SRS_KICKS.I : SRS_KICKS.JLSTZ;
                const kickKey = `${oldRot}>${newRot}`;
                const kickData = kicks[kickKey] || [[0, 0]];

                for (const [kx, ky] of kickData) {
                    if (!this.checkCollision(this.currentPiece, kx, -ky)) {
                        this.currentPiece.x += kx;
                        this.currentPiece.y -= ky;
                        return true;
                    }
                }

                this.currentPiece.rotation = oldRot;
                return false;
            }

            moveLeft() {
                if (!this.currentPiece) return false;
                if (!this.checkCollision(this.currentPiece, -1, 0)) {
                    this.currentPiece.x--;
                    return true;
                }
                return false;
            }

            moveRight() {
                if (!this.currentPiece) return false;
                if (!this.checkCollision(this.currentPiece, 1, 0)) {
                    this.currentPiece.x++;
                    return true;
                }
                return false;
            }

            moveDown() {
                if (!this.currentPiece) return false;
                if (!this.checkCollision(this.currentPiece, 0, 1)) {
                    this.currentPiece.y++;
                    this.score += 1;
                    return true;
                }
                return false;
            }

            hardDrop() {
                if (!this.currentPiece) return;
                let dropDist = 0;
                while (!this.checkCollision(this.currentPiece, 0, 1)) {
                    this.currentPiece.y++;
                    dropDist++;
                }
                this.score += dropDist * 2;
                this.lockPiece();
            }

            holdPiece_() {
                if (!this.canHold || !this.currentPiece) return;

                this.canHold = false;
                const type = this.currentPiece.type;

                if (this.holdPiece) {
                    const holdType = this.holdPiece.type;
                    this.holdPiece = new Tetromino(type);
                    this.currentPiece = new Tetromino(holdType);
                    this.currentPiece.x = Math.floor(COLS / 2) - Math.floor(this.currentPiece.getCurrentShape()[0].length / 2);
                    this.currentPiece.y = 0;
                } else {
                    this.holdPiece = new Tetromino(type);
                    this.spawnPiece();
                }

                this.drawHold();
            }

            getGhostY() {
                if (!this.currentPiece) return 0;
                let ghostY = this.currentPiece.y;
                while (!this.checkCollision(this.currentPiece, 0, ghostY - this.currentPiece.y + 1)) {
                    ghostY++;
                }
                return ghostY;
            }

            lockPiece() {
                if (!this.currentPiece) return;

                const shape = this.currentPiece.getCurrentShape();
                for (let y = 0; y < shape.length; y++) {
                    for (let x = 0; x < shape[y].length; x++) {
                        if (shape[y][x]) {
                            const by = this.currentPiece.y + y;
                            const bx = this.currentPiece.x + x;
                            if (by >= 0 && by < ROWS && bx >= 0 && bx < COLS) {
                                this.board[by][bx] = this.currentPiece.type;
                            }
                        }
                    }
                }

                this.clearLines();
                this.spawnPiece();
            }

            clearLines() {
                let cleared = 0;
                for (let y = ROWS - 1; y >= 0; y--) {
                    if (this.board[y].every(cell => cell !== EMPTY)) {
                        this.board.splice(y, 1);
                        this.board.unshift(Array(COLS).fill(EMPTY));
                        cleared++;
                        y++;
                    }
                }

                if (cleared > 0) {
                    const points = [0, 100, 300, 500, 800];
                    this.score += points[cleared] * this.level;
                    this.lines += cleared;

                    if (this.lines >= this.level * 10) {
                        this.level++;
                        this.dropInterval = Math.max(100, 800 - (this.level - 1) * 70);
                    }

                    this.updateStats();
                }
            }

            updateStats() {
                this.scoreEl.textContent = this.score.toLocaleString();
                this.levelEl.textContent = this.level;
                this.linesEl.textContent = this.lines;
            }

            update(timestamp) {
                if (this.gameOver) return;

                if (timestamp - this.lastDrop > this.dropInterval) {
                    if (!this.moveDown()) {
                        this.lockPiece();
                    }
                    this.lastDrop = timestamp;
                }
            }

            // ============================================
            // 渲染方法 - 霓虹发光风格
            // ============================================
            draw() {
                this.ctx.fillStyle = COLORS.grid;
                this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

                // 绘制网格线
                this.ctx.strokeStyle = COLORS.gridLine;
                this.ctx.lineWidth = 0.5;
                for (let x = 0; x <= COLS; x++) {
                    this.ctx.beginPath();
                    this.ctx.moveTo(x * BLOCK_SIZE, 0);
                    this.ctx.lineTo(x * BLOCK_SIZE, ROWS * BLOCK_SIZE);
                    this.ctx.stroke();
                }
                for (let y = 0; y <= ROWS; y++) {
                    this.ctx.beginPath();
                    this.ctx.moveTo(0, y * BLOCK_SIZE);
                    this.ctx.lineTo(COLS * BLOCK_SIZE, y * BLOCK_SIZE);
                    this.ctx.stroke();
                }

                // 绘制已锁定的方块
                for (let y = 0; y < ROWS; y++) {
                    for (let x = 0; x < COLS; x++) {
                        if (this.board[y][x] !== EMPTY) {
                            this.drawBlock(this.ctx, x, y, COLORS[this.board[y][x]], BLOCK_SIZE);
                        }
                    }
                }

                // 绘制幽灵方块
                if (this.currentPiece) {
                    const ghostY = this.getGhostY();
                    const shape = this.currentPiece.getCurrentShape();
                    this.ctx.globalAlpha = 0.25;
                    for (let y = 0; y < shape.length; y++) {
                        for (let x = 0; x < shape[y].length; x++) {
                            if (shape[y][x]) {
                                this.drawGhostBlock(this.ctx, this.currentPiece.x + x, ghostY + y, this.currentPiece.color);
                            }
                        }
                    }
                    this.ctx.globalAlpha = 1;

                    // 绘制当前方块
                    for (let y = 0; y < shape.length; y++) {
                        for (let x = 0; x < shape[y].length; x++) {
                            if (shape[y][x]) {
                                this.drawBlock(this.ctx, this.currentPiece.x + x, this.currentPiece.y + y, this.currentPiece.color, BLOCK_SIZE);
                            }
                        }
                    }
                }

                // 游戏结束覆盖
                if (this.gameOver) {
                    this.ctx.fillStyle = 'rgba(10, 10, 15, 0.85)';
                    this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
                    
                    this.ctx.fillStyle = '#ff006e';
                    this.ctx.font = 'bold 14px Orbitron';
                    this.ctx.textAlign = 'center';
                    this.ctx.fillText('GAME', this.canvas.width / 2, this.canvas.height / 2 - 10);
                    this.ctx.fillText('OVER', this.canvas.width / 2, this.canvas.height / 2 + 12);
                }
            }

            drawBlock(ctx, x, y, color, size) {
                const px = x * size;
                const py = y * size;
                const padding = 1;

                // 发光效果
                ctx.shadowColor = color.glow;
                ctx.shadowBlur = 8;

                // 主体
                ctx.fillStyle = color.main;
                ctx.fillRect(px + padding, py + padding, size - padding * 2, size - padding * 2);

                // 高对比度边缘 - 顶部和左侧高光
                ctx.shadowBlur = 0;
                ctx.fillStyle = 'rgba(255, 255, 255, 0.35)';
                ctx.fillRect(px + padding, py + padding, size - padding * 2, 2);
                ctx.fillRect(px + padding, py + padding, 2, size - padding * 2);

                // 底部和右侧阴影
                ctx.fillStyle = color.dark;
                ctx.fillRect(px + padding, py + size - padding - 2, size - padding * 2, 2);
                ctx.fillRect(px + size - padding - 2, py + padding, 2, size - padding * 2);

                // 内部高光
                ctx.fillStyle = 'rgba(255, 255, 255, 0.15)';
                ctx.fillRect(px + padding + 3, py + padding + 3, size - padding * 2 - 6, size - padding * 2 - 6);
            }

            drawGhostBlock(ctx, x, y, color) {
                const px = x * BLOCK_SIZE;
                const py = y * BLOCK_SIZE;
                const padding = 2;

                ctx.strokeStyle = color.main;
                ctx.lineWidth = 1.5;
                ctx.setLineDash([3, 3]);
                ctx.strokeRect(px + padding, py + padding, BLOCK_SIZE - padding * 2, BLOCK_SIZE - padding * 2);
                ctx.setLineDash([]);
            }

            drawNext() {
                const ctx = this.nextCtx;
                ctx.fillStyle = '#0d0d14';
                ctx.fillRect(0, 0, this.nextCanvas.width, this.nextCanvas.height);

                const previewSize = 16;
                let offsetY = 5;

                for (let i = 0; i < this.nextPieces.length; i++) {
                    const piece = this.nextPieces[i];
                    const shape = piece.shape[0];
                    const color = piece.color;

                    const pieceWidth = shape[0].length * previewSize;
                    const pieceHeight = shape.length * previewSize;
                    const offsetX = (this.nextCanvas.width - pieceWidth) / 2;

                    for (let y = 0; y < shape.length; y++) {
                        for (let x = 0; x < shape[y].length; x++) {
                            if (shape[y][x]) {
                                this.drawSmallBlock(ctx, offsetX + x * previewSize, offsetY + y * previewSize, color, previewSize);
                            }
                        }
                    }

                    offsetY += pieceHeight + 12;
                }
            }

            drawSmallBlock(ctx, x, y, color, size) {
                const padding = 1;
                
                ctx.shadowColor = color.glow;
                ctx.shadowBlur = 4;
                ctx.fillStyle = color.main;
                ctx.fillRect(x + padding, y + padding, size - padding * 2, size - padding * 2);
                
                ctx.shadowBlur = 0;
                ctx.fillStyle = 'rgba(255, 255, 255, 0.3)';
                ctx.fillRect(x + padding, y + padding, size - padding * 2, 1);
            }

            drawHold() {
                const ctx = this.holdCtx;
                ctx.fillStyle = '#0d0d14';
                ctx.fillRect(0, 0, this.holdCanvas.width, this.holdCanvas.height);

                if (!this.holdPiece) return;

                const piece = this.holdPiece;
                const shape = piece.shape[0];
                const color = piece.color;
                const previewSize = 18;

                const pieceWidth = shape[0].length * previewSize;
                const pieceHeight = shape.length * previewSize;
                const offsetX = (this.holdCanvas.width - pieceWidth) / 2;
                const offsetY = (this.holdCanvas.height - pieceHeight) / 2;

                if (!this.canHold) {
                    ctx.globalAlpha = 0.4;
                }

                for (let y = 0; y < shape.length; y++) {
                    for (let x = 0; x < shape[y].length; x++) {
                        if (shape[y][x]) {
                            this.drawSmallBlock(ctx, offsetX + x * previewSize, offsetY + y * previewSize, color, previewSize);
                        }
                    }
                }

                ctx.globalAlpha = 1;
            }

            restart() {
                this.board = this.createBoard();
                this.score = 0;
                this.level = 1;
                this.lines = 0;
                this.currentPiece = null;
                this.nextPieces = [];
                this.holdPiece = null;
                this.canHold = true;
                this.gameOver = false;
                this.lastDrop = 0;
                this.dropInterval = 800;
                this.bag = [];

                for (let i = 0; i < PREVIEW_COUNT; i++) {
                    this.nextPieces.push(this.getNextFromBag());
                }

                this.spawnPiece();
                this.updateStats();
                this.draw();
            }
        }

        // ============================================
        // 游戏管理器
        // ============================================
        class GameManager {
            constructor() {
                this.player1 = new TetrisGame('board1', 'next1', 'hold1', 'score1', 'level1', 'lines1', 1);
                this.player2 = new TetrisGame('board2', 'next2', 'hold2', 'score2', 'level2', 'lines2', 2);
                this.gameStarted = true;
                this.winner = null;

                this.setupControls();
                this.gameLoop();

                document.getElementById('restartBtn').addEventListener('click', () => {
                    this.restart();
                });
            }

            setupControls() {
                document.addEventListener('keydown', (e) => {
                    if (!this.gameStarted) return;

                    // Player 1: WASD + Space + Q
                    switch(e.key.toLowerCase()) {
                        case 'a': this.player1.moveLeft(); break;
                        case 'd': this.player1.moveRight(); break;
                        case 's': this.player1.moveDown(); break;
                        case 'w': this.player1.rotatePiece(); break;
                        case ' ': e.preventDefault(); this.player1.hardDrop(); break;
                        case 'q': this.player1.holdPiece_(); break;
                    }

                    // Player 2: Arrows + Enter + Shift
                    switch(e.key) {
                        case 'ArrowLeft': e.preventDefault(); this.player2.moveLeft(); break;
                        case 'ArrowRight': e.preventDefault(); this.player2.moveRight(); break;
                        case 'ArrowDown': e.preventDefault(); this.player2.moveDown(); break;
                        case 'ArrowUp': e.preventDefault(); this.player2.rotatePiece(); break;
                        case 'Enter': e.preventDefault(); this.player2.hardDrop(); break;
                        case 'Shift': e.preventDefault(); this.player2.holdPiece_(); break;
                    }
                });
            }

            checkGameEnd() {
                if (this.player1.gameOver && !this.player2.gameOver) {
                    this.winner = 2;
                    return true;
                }
                if (this.player2.gameOver && !this.player1.gameOver) {
                    this.winner = 1;
                    return true;
                }
                if (this.player1.gameOver && this.player2.gameOver) {
                    this.winner = this.player1.score > this.player2.score ? 1 : 
                                   this.player2.score > this.player1.score ? 2 : 0;
                    return true;
                }
                return false;
            }

            showGameStatus() {
                const statusEl = document.getElementById('gameStatus');
                const titleEl = document.getElementById('statusTitle');

                if (this.winner === 1) {
                    titleEl.textContent = 'PLAYER 1 WINS!';
                    titleEl.className = 'status-title p1-win';
                } else if (this.winner === 2) {
                    titleEl.textContent = 'PLAYER 2 WINS!';
                    titleEl.className = 'status-title p2-win';
                } else {
                    titleEl.textContent = 'DRAW!';
                    titleEl.className = 'status-title';
                }

                statusEl.classList.add('show');
            }

            restart() {
                this.player1.restart();
                this.player2.restart();
                this.winner = null;
                document.getElementById('gameStatus').classList.remove('show');
            }

            gameLoop() {
                const loop = (timestamp) => {
                    this.player1.update(timestamp);
                    this.player2.update(timestamp);

                    this.player1.draw();
                    this.player2.draw();

                    if (!this.winner && this.checkGameEnd()) {
                        this.showGameStatus();
                    }

                    requestAnimationFrame(loop);
                };
                requestAnimationFrame(loop);
            }
        }

        // 启动游戏
        window.addEventListener('DOMContentLoaded', () => {
            new GameManager();
        });
    </script>
</body>
</html>
```

## 实现说明

### 主要功能完成：

1. **双人分屏布局**
   - 左右两个完整的游戏区域
   - 中间VS分隔符
   - 响应式布局支持

2. **Canvas霓虹渲染**
   - 高对比度边缘效果（顶部高光、底部阴影）
   - 方块发光效果（shadowBlur）
   - 内部高光细节
   - 幽灵方块虚线预览

3. **3个预览方块**
   - Next区域显示接下来3个方块
   - 小尺寸方块渲染保持视觉一致

4. **Hold区域**
   - 支持暂存当前方块
   - 已使用时显示为半透明

5. **实时数据显示**
   - Score（金色） / Level（青色） / Lines（粉色）
   - 不同颜色发光效果区分

6. **完整游戏逻辑**
   - SRS旋转系统 + 踢墙
   - 7-bag随机算法
   - 消行计分与升级
   - 硬降落/软降落

7. **控制系统**
   - P1: WASD移动/旋转, Space硬降, Q暂存
   - P2: 方向键, Enter硬降, Shift暂存