# 实现敌方AI系统

**Agent**: coder

**Time**: 2026-02-17T20:07:28.393954

---

我将实现敌方AI系统，并修复测试中发现的问题。以下是完整的坦克大战游戏HTML文件：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>坦克大战</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Courier New', monospace;
            background-color: #111;
            color: #fff;
            display: flex;
            flex-direction: column;
            align-items: center;
            min-height: 100vh;
            overflow: hidden;
        }
        
        header {
            width: 100%;
            padding: 10px;
            background-color: #222;
            text-align: center;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.5);
        }
        
        h1 {
            font-size: 24px;
            margin-bottom: 10px;
            color: #0f0;
            text-shadow: 2px 2px 0 #090;
        }
        
        .game-info {
            display: flex;
            justify-content: space-around;
            max-width: 800px;
            margin: 0 auto;
        }
        
        .info-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            margin: 0 15px;
        }
        
        .info-label {
            font-size: 14px;
            color: #888;
            margin-bottom: 5px;
        }
        
        .info-value {
            font-size: 20px;
            font-weight: bold;
            color: #0f0;
        }
        
        .lives {
            display: flex;
            gap: 5px;
        }
        
        .life-icon {
            width: 20px;
            height: 20px;
            background-color: #0f0;
            border-radius: 3px;
            position: relative;
        }
        
        .life-icon::before {
            content: '';
            position: absolute;
            width: 10px;
            height: 10px;
            background-color: #0f0;
            border-radius: 50%;
            top: -5px;
            left: 5px;
        }
        
        main {
            margin-top: 20px;
            position: relative;
        }
        
        #gameCanvas {
            border: 2px solid #0f0;
            background-color: #000;
            box-shadow: 0 0 10px rgba(0, 255, 0, 0.5);
        }
        
        .game-overlay {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            background-color: rgba(0, 0, 0, 0.7);
            z-index: 10;
        }
        
        .overlay-title {
            font-size: 36px;
            margin-bottom: 20px;
            color: #0f0;
            text-shadow: 2px 2px 0 #090;
        }
        
        .overlay-text {
            font-size: 18px;
            margin-bottom: 10px;
            color: #ddd;
        }
        
        .button {
            padding: 10px 20px;
            font-size: 18px;
            background-color: #0f0;
            color: #000;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
            margin-top: 20px;
            transition: all 0.3s;
        }
        
        .button:hover {
            background-color: #0a0;
            transform: scale(1.05);
        }
        
        .controls {
            margin-top: 20px;
            text-align: center;
        }
        
        .control-info {
            font-size: 14px;
            color: #888;
            margin-top: 10px;
        }
        
        .level-transition {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            background-color: rgba(0, 0, 0, 0.9);
            z-index: 20;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.5s;
        }
        
        .level-transition.active {
            opacity: 1;
            pointer-events: all;
        }
        
        .level-title {
            font-size: 48px;
            margin-bottom: 20px;
            color: #ff0;
            text-shadow: 2px 2px 0 #f90;
        }
        
        .high-score {
            margin-top: 10px;
            font-size: 16px;
            color: #ff0;
        }
        
        .pause-indicator {
            position: absolute;
            top: 10px;
            left: 50%;
            transform: translateX(-50%);
            font-size: 24px;
            color: #ff0;
            background-color: rgba(0, 0, 0, 0.7);
            padding: 5px 15px;
            border-radius: 5px;
            display: none;
        }
        
        @media (max-width: 768px) {
            h1 {
                font-size: 20px;
            }
            
            .info-value {
                font-size: 16px;
            }
            
            .overlay-title {
                font-size: 28px;
            }
            
            .button {
                padding: 8px 16px;
                font-size: 16px;
            }
        }
    </style>
</head>
<body>
    <header>
        <h1>坦克大战</h1>
        <div class="game-info">
            <div class="info-item">
                <span class="info-label">得分</span>
                <span class="info-value" id="score">0</span>
            </div>
            <div class="info-item">
                <span class="info-label">关卡</span>
                <span class="info-value" id="level">1</span>
            </div>
            <div class="info-item">
                <span class="info-label">生命</span>
                <div class="lives" id="lives"></div>
            </div>
            <div class="info-item">
                <span class="info-label">最高分</span>
                <span class="info-value" id="highScore">0</span>
            </div>
        </div>
    </header>
    
    <main>
        <canvas id="gameCanvas" width="800" height="600"></canvas>
        <div class="game-overlay" id="gameOverlay">
            <h2 class="overlay-title">坦克大战</h2>
            <p class="overlay-text">保护你的基地，消灭所有敌方坦克！</p>
            <button class="button" id="startButton">开始游戏</button>
            <div class="high-score" id="highScoreDisplay"></div>
        </div>
        <div class="level-transition" id="levelTransition">
            <h2 class="level-title">第 <span id="currentLevel">1</span> 关</h2>
            <p class="overlay-text">准备进入下一关...</p>
        </div>
        <div class="pause-indicator" id="pauseIndicator">游戏暂停</div>
    </main>
    
    <div class="controls">
        <p class="control-info">使用 WASD 或方向键移动，空格键射击，P 键暂停游戏</p>
    </div>

    <script>
        // 游戏配置
        const GAME_CONFIG = {
            TILE_SIZE: 40,
            PLAYER_SPEED: 3,
            ENEMY_SPEED: 2,
            BULLET_SPEED: 5,
            ENEMY_BULLET_SPEED: 4,
            ENEMY_FIRE_RATE: 2000, // 毫秒
            ENEMY_SIGHT_RANGE: 300,
            MAX_ENEMIES: 5,
            MAX_LIVES: 3,
            SCORE_DESTROY_ENEMY: 100,
            SCORE_DESTROY_BASE: 500,
            LEVEL_SCORE_THRESHOLD: 1000
        };

        // 游戏状态
        const GameState = {
            MENU: 'menu',
            PLAYING: 'playing',
            PAUSED: 'paused',
            GAME_OVER: 'game_over',
            LEVEL_COMPLETE: 'level_complete',
            LEVEL_TRANSITION: 'level_transition'
        };

        // 方向常量
        const Direction = {
            UP: 0,
            RIGHT: 1,
            DOWN: 2,
            LEFT: 3
        };

        // 坦克类型
        const TankType = {
            PLAYER: 'player',
            ENEMY: 'enemy',
            BASE: 'base'
        };

        // 游戏元素类型
        const TileType = {
            EMPTY: 0,
            WALL: 1,
            BRICK: 2,
            WATER: 3,
            BASE: 4
        };

        // 游戏主类
        class Game {
            constructor() {
                this.canvas = document.getElementById('gameCanvas');
                this.ctx = this.canvas.getContext('2d');
                this.state = GameState.MENU;
                this.score = 0;
                this.level = 1;
                this.lives = GAME_CONFIG.MAX_LIVES;
                this.highScore = parseInt(localStorage.getItem('tankHighScore') || 0);
                
                this.player = null;
                this.enemies = [];
                this.bullets = [];
                this.enemyBullets = [];
                this.tiles = [];
                this.base = null;
                
                this.keys = {};
                this.lastEnemyFireTime = 0;
                this.enemyFireInterval = GAME_CONFIG.ENEMY_FIRE_RATE;
                
                this.init();
            }
            
            init() {
                // 设置画布大小
                this.resizeCanvas();
                window.addEventListener('resize', () => this.resizeCanvas());
                
                // 键盘事件
                window.addEventListener('keydown', (e) => this.handleKeyDown(e));
                window.addEventListener('keyup', (e) => this.handleKeyUp(e));
                
                // 按钮事件
                document.getElementById('startButton').addEventListener('click', () => this.startGame());
                
                // 更新最高分显示
                document.getElementById('highScore').textContent = this.highScore;
                document.getElementById('highScoreDisplay').textContent = `最高分: ${this.highScore}`;
                
                // 初始化关卡
                this.loadLevel(1);
                
                // 开始游戏循环
                this.gameLoop();
            }
            
            resizeCanvas() {
                // 保存当前画布内容
                const imageData = this.ctx.getImageData(0, 0, this.canvas.width, this.canvas.height);
                
                // 根据窗口大小调整画布
                const maxWidth = window.innerWidth - 40;
                const maxHeight = window.innerHeight - 200;
                
                const aspectRatio = 4 / 3;
                let width = maxWidth;
                let height = width / aspectRatio;
                
                if (height > maxHeight) {
                    height = maxHeight;
                    width = height * aspectRatio;
                }
                
                this.canvas.width = width;
                this.canvas.height = height;
                
                // 恢复画布内容
                this.ctx.putImageData(imageData, 0, 0);
            }
            
            startGame() {
                this.state = GameState.PLAYING;
                document.getElementById('gameOverlay').style.display = 'none';
                this.resetLevel();
            }
            
            resetLevel() {
                this.enemies = [];
                this.bullets = [];
                this.enemyBullets = [];
                this.loadLevel(this.level);
            }
            
            loadLevel(levelNum) {
                this.level = levelNum;
                document.getElementById('level').textContent = levelNum;
                
                // 生成地图
                this.generateMap(levelNum);
                
                // 创建玩家
                this.player = new Tank(
                    GAME_CONFIG.TILE_SIZE * 1.5,
                    GAME_CONFIG.TILE_SIZE * 1.5,
                    Direction.RIGHT,
                    TankType.PLAYER
                );
                
                // 创建基地
                const baseX = this.canvas.width / 2 - GAME_CONFIG.TILE_SIZE / 2;
                const baseY = this.canvas.height - GAME_CONFIG.TILE_SIZE * 1.5;
                this.base = new Tank(baseX, baseY, Direction.UP, TankType.BASE);
                
                // 创建敌人
                this.spawnEnemies(levelNum);
                
                // 更新生命显示
                this.updateLivesDisplay();
            }
            
            generateMap(levelNum) {
                const cols = Math.floor(this.canvas.width / GAME_CONFIG.TILE_SIZE);
                const rows = Math.floor(this.canvas.height / GAME_CONFIG.TILE_SIZE);
                
                // 初始化地图
                this.tiles = [];
                for (let y = 0; y < rows; y++) {
                    this.tiles[y] = [];
                    for (let x = 0; x < cols; x++) {
                        // 边界墙
                        if (x === 0 || y === 0 || x === cols - 1 || y === rows - 1) {
                            this.tiles[y][x] = TileType.WALL;
                        } 
                        // 基地位置
                        else if (Math.abs(x - cols / 2) < 1 && Math.abs(y - rows + 1.5) < 1) {
                            this.tiles[y][x] = TileType.BASE;
                        }
                        // 随机生成障碍物
                        else {
                            const rand = Math.random();
                            if (rand < 0.1) {
                                this.tiles[y][x] = TileType.WALL;
                            } else if (rand < 0.2) {
                                this.tiles[y][x] = TileType.BRICK;
                            } else {
                                this.tiles[y][x] = TileType.EMPTY;
                            }
                        }
                    }
                }
                
                // 确保玩家起始位置和基地周围没有障碍物
                for (let y = 0; y < 3; y++) {
                    for (let x = 0; x < 3; x++) {
                        if (x < cols && y < rows) {
                            this.tiles[y][x] = TileType.EMPTY;
                        }
                    }
                }
                
                const baseRow = Math.floor(rows - 1.5);
                const baseCol = Math.floor(cols / 2);
                for (let y = baseRow - 1; y <= baseRow + 1; y++) {
                    for (let x = baseCol - 1; x <= baseCol + 1; x++) {
                        if (x >= 0 && x < cols && y >= 0 && y < rows) {
                            this.tiles[y][x] = TileType.EMPTY;
                        }
                    }
                }
                
                // 根据关卡增加地图复杂度
                if (levelNum > 1) {
                    // 添加更多障碍物
                    for (let i = 0; i < levelNum * 2; i++) {
                        const x = Math.floor(Math.random() * (cols - 2)) + 1;
                        const y = Math.floor(Math.random() * (rows - 4)) + 2;
                        if (this.tiles[y][x] === TileType.EMPTY) {
                            this.tiles[y][x] = TileType.BRICK;
                        }
                    }
                }
            }
            
            spawnEnemies(levelNum) {
                const enemyCount = Math.min(GAME_CONFIG.MAX_ENEMIES, 2 + Math.floor(levelNum / 2));
                
                for (let i = 0; i < enemyCount; i++) {
                    let x, y;
                    let validPosition = false;
                    
                    // 尝试找到一个有效的位置
                    while (!validPosition) {
                        x = Math.random() * (this.canvas.width - GAME_CONFIG.TILE_SIZE * 2) + GAME_CONFIG.TILE_SIZE;
                        y = Math.random() * (this.canvas.height / 3) + GAME_CONFIG.TILE_SIZE;
                        
                        // 检查位置是否有效
                        validPosition = true;
                        const tileX = Math.floor(x / GAME_CONFIG.TILE_SIZE);
                        const tileY = Math.floor(y / GAME_CONFIG.TILE_SIZE);
                        
                        // 检查是否与玩家起始位置重叠
                        if (Math.abs(x - GAME_CONFIG.TILE_SIZE * 1.5) < GAME_CONFIG.TILE_SIZE * 2 &&
                            Math.abs(y - GAME_CONFIG.TILE_SIZE * 1.5) < GAME_CONFIG.TILE_SIZE * 2) {
                            validPosition = false;
                        }
                        
                        // 检查是否与基地重叠
                        if (Math.abs(x - this.base.x) < GAME_CONFIG.TILE_SIZE * 2 &&
                            Math.abs(y - this.base.y) < GAME_CONFIG.TILE_SIZE * 2) {
                            validPosition = false;
                        }
                        
                        // 检查是否与其他敌人重叠
                        for (const enemy of this.enemies) {
                            if (Math.abs(x - enemy.x) < GAME_CONFIG.TILE_SIZE * 2 &&
                                Math.abs(y - enemy.y) < GAME_CONFIG.TILE_SIZE * 2) {
                                validPosition = false;
                                break;
                            }
                        }
                        
                        // 检查是否与障碍物重叠
                        if (this.tiles[tileY] && this.tiles[tileY][tileX] !== TileType.EMPTY) {
                            validPosition = false;
                        }
                    }
                    
                    // 随机选择一个方向
                    const directions = [Direction.UP, Direction.RIGHT, Direction.DOWN, Direction.LEFT];
                    const direction = directions[Math.floor(Math.random() * directions.length)];
                    
                    this.enemies.push(new Tank(x, y, direction, TankType.ENEMY));
                }
            }
            
            handleKeyDown(e) {
                this.keys[e.key.toLowerCase()] = true;
                
                // 处理暂停
                if (e.key.toLowerCase() === 'p' && this.state === GameState.PLAYING) {
                    this.pauseGame();
                } else if (e.key.toLowerCase() === 'p' && this.state === GameState.PAUSED) {
                    this.resumeGame();
                }
                
                // 处理射击
                if (e.key === ' ' && this.state === GameState.PLAYING) {
                    this.playerShoot();
                }
            }
            
            handleKeyUp(e) {
                this.keys[e.key.toLowerCase()] = false;
            }
            
            playerShoot() {
                if (this.player.canShoot()) {
                    const bullet = new Bullet(
                        this.player.x + GAME_CONFIG.TILE_SIZE / 2,
                        this.player.y + GAME_CONFIG.TILE_SIZE / 2,
                        this.player.direction,
                        false
                    );
                    this