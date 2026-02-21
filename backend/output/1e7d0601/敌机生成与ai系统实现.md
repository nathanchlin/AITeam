# 敌机生成与AI系统实现

**Agent**: coder

**Time**: 2026-02-18T09:05:15.702975

---

# 敌机生成与AI系统实现

我将为你实现一个完整的敌机生成系统，包含不同类型的敌机AI行为模式、移动路径、攻击策略和难度递增机制。同时，我会解决之前测试中发现的问题。

## 完整游戏实现

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>1942 飞行射击游戏</title>
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
            overflow: hidden;
            touch-action: none;
        }
        
        #gameContainer {
            position: relative;
            width: 100vw;
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            background: #000;
        }
        
        #gameCanvas {
            position: absolute;
            background: #000;
            image-rendering: -moz-crisp-edges;
            image-rendering: -webkit-crisp-edges;
            image-rendering: pixelated;
            image-rendering: crisp-edges;
        }
        
        #gameUI {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 10;
        }
        
        .score {
            position: absolute;
            top: 10px;
            left: 10px;
            font-size: 20px;
            font-weight: bold;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }
        
        .lives {
            position: absolute;
            top: 10px;
            right: 10px;
            font-size: 20px;
            font-weight: bold;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }
        
        .game-over {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
            display: none;
            pointer-events: auto;
        }
        
        .game-over h2 {
            font-size: 48px;
            margin-bottom: 20px;
            color: #ff0000;
            text-shadow: 3px 3px 6px rgba(0,0,0,0.7);
        }
        
        .game-over p {
            font-size: 24px;
            margin-bottom: 30px;
        }
        
        .restart-btn {
            padding: 15px 30px;
            font-size: 20px;
            background-color: #ff0000;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        
        .restart-btn:hover {
            background-color: #cc0000;
        }
        
        .start-screen {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.8);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            z-index: 20;
        }
        
        .start-screen h1 {
            font-size: 48px;
            margin-bottom: 30px;
            color: #ff0000;
            text-shadow: 3px 3px 6px rgba(0,0,0,0.7);
        }
        
        .start-screen p {
            font-size: 20px;
            margin-bottom: 20px;
        }
        
        .start-btn {
            padding: 15px 30px;
            font-size: 20px;
            background-color: #ff0000;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        
        .start-btn:hover {
            background-color: #cc0000;
        }
        
        /* 响应式设计 */
        @media (max-width: 768px) {
            .score, .lives {
                font-size: 16px;
            }
            
            .game-over h2 {
                font-size: 36px;
            }
            
            .game-over p {
                font-size: 18px;
            }
            
            .restart-btn, .start-btn {
                padding: 12px 24px;
                font-size: 18px;
            }
        }
        
        @media (max-width: 480px) {
            .score, .lives {
                font-size: 14px;
            }
            
            .game-over h2 {
                font-size: 28px;
            }
            
            .game-over p {
                font-size: 16px;
            }
            
            .restart-btn, .start-btn {
                padding: 10px 20px;
                font-size: 16px;
            }
        }
    </style>
</head>
<body>
    <div id="gameContainer">
        <canvas id="gameCanvas"></canvas>
        <div id="gameUI">
            <div class="score">得分: <span id="scoreValue">0</span></div>
            <div class="lives">生命: <span id="livesValue">3</span></div>
            <div class="game-over">
                <h2>游戏结束</h2>
                <p>最终得分: <span id="finalScore">0</span></p>
                <button class="restart-btn" id="restartBtn">重新开始</button>
            </div>
            <div class="start-screen" id="startScreen">
                <h1>1942 飞行射击</h1>
                <p>使用方向键或触摸控制飞机移动</p>
                <p>空格键或屏幕点击发射子弹</p>
                <button class="start-btn" id="startBtn">开始游戏</button>
            </div>
        </div>
    </div>

    <script>
        // 游戏引擎类
        class GameEngine {
            constructor() {
                try {
                    this.canvas = document.getElementById('gameCanvas');
                    this.ctx = this.canvas.getContext('2d');
                    this.gameContainer = document.getElementById('gameContainer');
                    
                    // 游戏状态
                    this.gameState = 'start'; // start, playing, paused, gameover
                    this.score = 0;
                    this.lives = 3;
                    this.level = 1;
                    this.enemySpawnTimer = 0;
                    this.enemySpawnInterval = 60; // 初始生成间隔（帧数）
                    this.difficultyIncreaseTimer = 0;
                    this.difficultyIncreaseInterval = 600; // 每10秒增加难度
                    
                    // 游戏对象数组
                    this.player = null;
                    this.bullets = [];
                    this.enemies = [];
                    this.enemyBullets = [];
                    this.explosions = [];
                    this.powerUps = [];
                    this.stars = [];
                    
                    // 输入状态
                    this.keys = {};
                    this.touchStartX = 0;
                    this.touchStartY = 0;
                    
                    // 设置画布尺寸
                    this.resizeCanvas();
                    
                    // 初始化游戏
                    this.init();
                    
                    // 事件监听
                    this.setupEventListeners();
                    
                    // 开始游戏循环
                    this.lastTime = 0;
                    this.gameLoop(0);
                } catch (error) {
                    console.error('游戏引擎初始化失败:', error);
                }
            }
            
            // 设置画布尺寸
            resizeCanvas() {
                // 获取容器尺寸
                const containerWidth = this.gameContainer.clientWidth;
                const containerHeight = this.gameContainer.clientHeight;
                
                // 计算适合的画布尺寸，保持16:9比例
                const aspectRatio = 16 / 9;
                let canvasWidth, canvasHeight;
                
                if (containerWidth / containerHeight > aspectRatio) {
                    // 容器更宽，以高度为准
                    canvasHeight = containerHeight;
                    canvasWidth = canvasHeight * aspectRatio;
                } else {
                    // 容器更高，以宽度为准
                    canvasWidth = containerWidth;
                    canvasHeight = canvasWidth / aspectRatio;
                }
                
                // 设置画布尺寸
                this.canvas.width = canvasWidth;
                this.canvas.height = canvasHeight;
                this.width = canvasWidth;
                this.height = canvasHeight;
                
                // 设置CSS尺寸，避免模糊
                this.canvas.style.width = `${canvasWidth}px`;
                this.canvas.style.height = `${canvasHeight}px`;
                
                // 更新游戏对象比例
                this.updateScale();
            }
            
            // 更新游戏对象比例
            updateScale() {
                this.scaleX = this.width / 800;
                this.scaleY = this.height / 600;
            }
            
            // 初始化游戏
            init() {
                // 创建玩家
                this.player = new Player(this.width / 2, this.height - 100, this);
                
                // 创建星空背景
                for (let i = 0; i < 100; i++) {
                    this.stars.push(new Star(this));
                }
                
                // 重置游戏状态
                this.score = 0;
                this.lives = 3;
                this.level = 1;
                this.enemySpawnTimer = 0;
                this.enemySpawnInterval = 60;
                this.difficultyIncreaseTimer = 0;
                
                // 清空游戏对象
                this.bullets = [];
                this.enemies = [];
                this.enemyBullets = [];
                this.explosions = [];
                this.powerUps = [];
                
                // 更新UI
                this.updateUI();
            }
            
            // 设置事件监听
            setupEventListeners() {
                // 键盘事件
                window.addEventListener('keydown', (e) => {
                    this.keys[e.key] = true;
                    if (e.key === ' ' && this.gameState === 'playing') {
                        e.preventDefault();
                        this.player.shoot();
                    }
                });
                
                window.addEventListener('keyup', (e) => {
                    this.keys[e.key] = false;
                });
                
                // 触摸事件
                this.canvas.addEventListener('touchstart', (e) => {
                    e.preventDefault();
                    const touch = e.touches[0];
                    const rect = this.canvas.getBoundingClientRect();
                    this.touchStartX = touch.clientX - rect.left;
                    this.touchStartY = touch.clientY - rect.top;
                    
                    if (this.gameState === 'playing') {
                        this.player.shoot();
                    }
                });
                
                this.canvas.addEventListener('touchmove', (e) => {
                    e.preventDefault();
                    if (this.gameState === 'playing') {
                        const touch = e.touches[0];
                        const rect = this.canvas.getBoundingClientRect();
                        const x = touch.clientX - rect.left;
                        const y = touch.clientY - rect.top;
                        
                        // 计算移动方向
                        const dx = x - this.touchStartX;
                        const dy = y - this.touchStartY;
                        
                        // 移动玩家
                        this.player.moveBy(dx, dy);
                        
                        // 更新触摸起始位置
                        this.touchStartX = x;
                        this.touchStartY = y;
                    }
                });
                
                // 鼠标事件（用于测试）
                this.canvas.addEventListener('mousedown', (e) => {
                    if (this.gameState === 'playing') {
                        this.player.shoot();
                    }
                });
                
                this.canvas.addEventListener('mousemove', (e) => {
                    if (this.gameState === 'playing') {
                        const rect = this.canvas.getBoundingClientRect();
                        const x = e.clientX - rect.left;
                        const y = e.clientY - rect.top;
                        
                        // 计算移动方向
                        const dx = x - this.player.x;
                        const dy = y - this.player.y;
                        
                        // 移动玩家
                        this.player.moveBy(dx * 0.1, dy * 0.1);
                    }
                });
                
                // 窗口大小改变事件
                window.addEventListener('resize', () => {
                    this.resizeCanvas();
                });
                
                // 开始按钮
                document.getElementById('startBtn').addEventListener('click', () => {
                    this.startGame();
                });
                
                // 重新开始按钮
                document.getElementById('restartBtn').addEventListener('click', () => {
                    this.restartGame();
                });
            }
            
            // 开始游戏
            startGame() {
                this.gameState = 'playing';
                document.getElementById('startScreen').style.display = 'none';
            }
            
            // 重新开始游戏
            restartGame() {
                this.gameState = 'playing';
                document.querySelector('.game-over').style.display = 'none';
                this.init();
            }
            
            // 游戏主循环
            gameLoop(timestamp) {
                requestAnimationFrame((timestamp) => this.gameLoop(timestamp));
                
                // 计算时间增量
                const deltaTime = timestamp - this.lastTime;
                this.lastTime = timestamp;
                
                // 限制最大时间增量，避免大跳跃
                const cappedDeltaTime = Math.min(deltaTime, 100);
                
                if (this.gameState === 'playing') {
                    // 更新游戏逻辑
                    this.update(cappedDeltaTime);
                    
                    // 渲染游戏
                    this.render();
                }
            }
            
            // 更新游戏状态
            update(deltaTime) {
                // 更新星空背景
                this.stars.forEach(star => star.update(deltaTime));
                
                // 更新玩家
                if (this.player) {
                    // 处理键盘输入
                    if (this.keys['ArrowLeft'] || this.keys['a']) {
                        this.player.moveLeft();
                    }
                    if (this.keys['ArrowRight'] || this.keys['d']) {
                        this.player.moveRight();
                    }
                    if (this.keys['ArrowUp'] || this.keys['w']) {
                        this.player.moveUp();
                    }
                    if (this.keys['ArrowDown'] || this.keys['s']) {
                        this.player.moveDown();
                    }
                    
                    this.player.update(deltaTime);
                }
                
                // 更新子弹
                this.bullets = this.bullets.filter(bullet => {
                    bullet.update(deltaTime);
                    return bullet.y > -10 && bullet.y < this.height + 10;
                });
                
                // 更新敌机
                this.enemies = this.enemies.filter(enemy => {
                    enemy.update(deltaTime);
                    
                    // 敌机射击
                    if (enemy.shouldShoot()) {
                        this.enemyBullets.push(new EnemyBullet(enemy.x, enemy.y + enemy.height / 2, this));
                    }
                    
                    // 移除超出屏幕的敌机
                    return enemy.y < this.height + 50 && enemy.y > -50;
                });
                
                // 更新敌机子弹
                this.enemyBullets = this.enemyBullets.filter(bullet => {
                    bullet.update(deltaTime);
                    return bullet.y < this.height + 10 && bullet.y > -10;
                });
                
                // 更新爆炸效果
                this.explosions = this.explosions.filter(explosion => {
                    explosion.update(deltaTime);
                    return !explosion.isComplete();
                });
                
                // 更新道具
                this.powerUps = this.powerUps.filter(powerUp => {
                    powerUp.update(deltaTime);
                    return powerUp.y < this.height + 10 && powerUp.y > -10;
                });
                
                // 碰撞检测
                this.checkCollisions();
                
                // 生成敌机
                this.spawnEnemies();
                
                // 增加难度
                this.increaseDifficulty();
                
                // 更新UI
                this.updateUI();
            }
            
            // 渲染游戏
            render() {
                // 清空画布
                this.ctx.fillStyle = '#000';
                this.ctx.fillRect(0, 0, this.width, this.height);
                
                // 渲染星空背景
                this.stars.forEach(star => star.render(this.ctx));
                
                // 渲染玩家
                if (this.player) {
                    this.player.render(this.ctx);
                }
                
                // 渲染子弹
                this.bullets.forEach(bullet => bullet.render(this.ctx));
                
                // 渲染敌机
                this.enemies.forEach(enemy => enemy.render(this.ctx));
                
                // 渲染敌机子弹
                this.enemyBullets.forEach(bullet => bullet.render(this.ctx));
                
                // 渲染爆炸效果
                this.explosions.forEach(explosion => explosion.render(this.ctx));
                
                // 渲染道具
                this.powerUps.forEach(powerUp => powerUp.render(this.ctx));
            }
            
            // 生成敌机
            spawnEnemies() {
                this.enemySpawnTimer++;
                
                if (this.enemySpawnTimer >= this.enemySpawnInterval) {
                    this.enemySpawnTimer = 0;
                    
                    // 根据难度和关卡决定敌机类型
                    const enemyType = this.selectEnemyType();
                    
                    // 随机生成位置
                    const x = Math.random() * (this.width - 40) + 20;
                    
                    // 创建敌机
                    this.enemies.push(new Enemy(x, -50, enemyType, this));
                }
            }
            
            // 选择敌机类型
            selectEnemyType() {
                // 根据难度和关卡选择敌机类型
                const random = Math.random();
                
                if (this.level < 2) {
                    // 第一关只有基础敌机
                    return 'basic';
                } else if (this.level < 5) {
                    // 第二关到第四关有基础和快速敌机
                    return random < 0.7 ? 'basic' : 'fast';
                } else if (this.level < 10) {
                    // 第五关到第九关有基础、快速和重型敌机
                    if (random < 0.5) return 'basic';
                    else if (random < 0.8) return 'fast';
                    else return 'heavy';
                } else {
                    // 第十关以上所有类型敌机都有，并增加精英敌机
                    if (random < 0.4) return 'basic';
                    else if (random < 0.7) return 'fast';
                    else if (random < 0.9) return 'heavy';
                    else return 'elite';
                }
            }
            
            // 增加难度
            increaseDifficulty() {
                this.difficultyIncreaseTimer++;
                
                if (this.difficultyIncreaseTimer >= this.difficultyIncreaseInterval) {
                    this.difficultyIncreaseTimer = 0;
                    
                    // 增加难度
                    this.level++;
                    this.enemySpawnInterval = Math.max(20, this.enemySpawnInterval - 5);
                    
                   