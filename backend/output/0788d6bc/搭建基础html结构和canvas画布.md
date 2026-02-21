# 搭建基础HTML结构和Canvas画布

**Agent**: coder

**Time**: 2026-02-17T19:30:04.923600

---

我将为您搭建坦克大战游戏的基础HTML结构和Canvas画布。这是一个完整的HTML文件，包含了游戏的基本框架和初始化代码。

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
            font-family: 'Arial', sans-serif;
            background-color: #2c3e50;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            overflow: hidden;
        }

        .game-container {
            background-color: #34495e;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
            padding: 20px;
            position: relative;
        }

        .game-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            color: #ecf0f1;
            padding: 0 10px;
        }

        .game-title {
            font-size: 24px;
            font-weight: bold;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
        }

        .game-stats {
            display: flex;
            gap: 20px;
        }

        .stat-item {
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        .stat-label {
            font-size: 12px;
            color: #bdc3c7;
        }

        .stat-value {
            font-size: 18px;
            font-weight: bold;
            color: #f1c40f;
        }

        #gameCanvas {
            border: 3px solid #1a252f;
            background-color: #1a252f;
            display: block;
            image-rendering: pixelated;
            image-rendering: -moz-crisp-edges;
            image-rendering: crisp-edges;
        }

        .game-controls {
            margin-top: 15px;
            display: flex;
            justify-content: center;
            gap: 10px;
        }

        .control-btn {
            background-color: #3498db;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 10px 20px;
            font-size: 16px;
            cursor: pointer;
            transition: background-color 0.3s;
        }

        .control-btn:hover {
            background-color: #2980b9;
        }

        .control-btn:active {
            transform: scale(0.98);
        }

        .game-over-overlay {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.8);
            display: none;
            justify-content: center;
            align-items: center;
            flex-direction: column;
            border-radius: 10px;
            z-index: 10;
        }

        .game-over-title {
            font-size: 36px;
            color: #e74c3c;
            margin-bottom: 20px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
        }

        .final-score {
            font-size: 24px;
            color: #f1c40f;
            margin-bottom: 30px;
        }

        .instructions {
            position: absolute;
            bottom: -80px;
            left: 0;
            width: 100%;
            text-align: center;
            color: #bdc3c7;
            font-size: 14px;
        }

        .key-hint {
            display: inline-block;
            background-color: #2c3e50;
            border: 1px solid #34495e;
            border-radius: 3px;
            padding: 3px 8px;
            margin: 0 3px;
            font-family: monospace;
        }
    </style>
</head>
<body>
    <div class="game-container">
        <div class="game-header">
            <div class="game-title">坦克大战</div>
            <div class="game-stats">
                <div class="stat-item">
                    <span class="stat-label">得分</span>
                    <span class="stat-value" id="score">0</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">生命</span>
                    <span class="stat-value" id="lives">3</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">关卡</span>
                    <span class="stat-value" id="level">1</span>
                </div>
            </div>
        </div>
        
        <canvas id="gameCanvas" width="800" height="600"></canvas>
        
        <div class="game-controls">
            <button class="control-btn" id="startBtn">开始游戏</button>
            <button class="control-btn" id="pauseBtn">暂停</button>
            <button class="control-btn" id="restartBtn">重新开始</button>
        </div>
        
        <div class="game-over-overlay" id="gameOverOverlay">
            <div class="game-over-title">游戏结束</div>
            <div class="final-score">最终得分: <span id="finalScore">0</span></div>
            <button class="control-btn" id="playAgainBtn">再玩一次</button>
        </div>
        
        <div class="instructions">
            使用 <span class="key-hint">↑</span> <span class="key-hint">↓</span> <span class="key-hint">←</span> <span class="key-hint">→</span> 或 <span class="key-hint">W</span> <span class="key-hint">A</span> <span class="key-hint">S</span> <span class="key-hint">D</span> 移动，<span class="key-hint">空格</span> 射击
        </div>
    </div>

    <script>
        // 游戏配置
        const GAME_CONFIG = {
            canvasWidth: 800,
            canvasHeight: 600,
            tileSize: 40,
            playerSpeed: 3,
            bulletSpeed: 5,
            enemySpeed: 1.5,
            enemyBulletSpeed: 4,
            maxEnemies: 5,
            enemySpawnInterval: 3000, // 3秒
            tankSize: 30,
            bulletSize: 4,
            wallHealth: {
                steel: 100,
                brick: 20
            }
        };

        // 游戏状态
        const gameState = {
            isRunning: false,
            isPaused: false,
            score: 0,
            lives: 3,
            level: 1,
            keys: {},
            lastTime: 0,
            deltaTime: 0,
            enemies: [],
            bullets: [],
            walls: [],
            powerUps: [],
            particles: []
        };

        // 获取Canvas和上下文
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');

        // 游戏对象类
        class GameObject {
            constructor(x, y, width, height) {
                this.x = x;
                this.y = y;
                this.width = width;
                this.height = height;
                this.active = true;
            }

            draw() {
                // 基础绘制方法，子类可以重写
            }

            update(deltaTime) {
                // 基础更新方法，子类可以重写
            }

            intersects(other) {
                return this.x < other.x + other.width &&
                       this.x + this.width > other.x &&
                       this.y < other.y + other.height &&
                       this.y + this.height > other.y;
            }
        }

        // 玩家坦克类
        class PlayerTank extends GameObject {
            constructor(x, y) {
                super(x, y, GAME_CONFIG.tankSize, GAME_CONFIG.tankSize);
                this.speed = GAME_CONFIG.playerSpeed;
                this.direction = 'up';
                this.canShoot = true;
                this.shootCooldown = 0;
                this.color = '#2ecc71';
            }

            draw() {
                ctx.save();
                ctx.translate(this.x + this.width / 2, this.y + this.height / 2);
                
                // 根据方向旋转坦克
                switch (this.direction) {
                    case 'up':
                        ctx.rotate(0);
                        break;
                    case 'right':
                        ctx.rotate(Math.PI / 2);
                        break;
                    case 'down':
                        ctx.rotate(Math.PI);
                        break;
                    case 'left':
                        ctx.rotate(-Math.PI / 2);
                        break;
                }
                
                // 绘制坦克主体
                ctx.fillStyle = this.color;
                ctx.fillRect(-this.width / 2, -this.height / 2, this.width, this.height);
                
                // 绘制坦克炮管
                ctx.fillStyle = '#27ae60';
                ctx.fillRect(0, -this.width / 8, this.width / 2, this.width / 4);
                
                // 绘制坦克细节
                ctx.fillStyle = '#1e8449';
                ctx.fillRect(-this.width / 4, -this.height / 4, this.width / 2, this.height / 2);
                
                ctx.restore();
            }

            update(deltaTime) {
                // 处理移动
                if (gameState.keys['ArrowUp'] || gameState.keys['w']) {
                    this.y -= this.speed;
                    this.direction = 'up';
                }
                if (gameState.keys['ArrowDown'] || gameState.keys['s']) {
                    this.y += this.speed;
                    this.direction = 'down';
                }
                if (gameState.keys['ArrowLeft'] || gameState.keys['a']) {
                    this.x -= this.speed;
                    this.direction = 'left';
                }
                if (gameState.keys['ArrowRight'] || gameState.keys['d']) {
                    this.x += this.speed;
                    this.direction = 'right';
                }
                
                // 边界检查
                this.x = Math.max(0, Math.min(canvas.width - this.width, this.x));
                this.y = Math.max(0, Math.min(canvas.height - this.height, this.y));
                
                // 射击冷却
                if (this.shootCooldown > 0) {
                    this.shootCooldown -= deltaTime;
                } else {
                    this.canShoot = true;
                }
                
                // 射击
                if (gameState.keys[' '] && this.canShoot) {
                    this.shoot();
                    this.canShoot = false;
                    this.shootCooldown = 300; // 300ms冷却时间
                }
            }
            
            shoot() {
                let bulletX = this.x + this.width / 2;
                let bulletY = this.y + this.height / 2;
                
                switch (this.direction) {
                    case 'up':
                        bulletY -= this.height / 2;
                        break;
                    case 'right':
                        bulletX += this.width / 2;
                        break;
                    case 'down':
                        bulletY += this.height / 2;
                        break;
                    case 'left':
                        bulletX -= this.width / 2;
                        break;
                }
                
                gameState.bullets.push(new Bullet(bulletX, bulletY, this.direction, 'player'));
            }
        }

        // 敌方坦克类
        class EnemyTank extends GameObject {
            constructor(x, y) {
                super(x, y, GAME_CONFIG.tankSize, GAME_CONFIG.tankSize);
                this.speed = GAME_CONFIG.enemySpeed;
                this.direction = this.getRandomDirection();
                this.canShoot = true;
                this.shootCooldown = 0;
                this.shootInterval = 1000 + Math.random() * 2000; // 1-3秒随机射击间隔
                this.moveTimer = 0;
                this.moveInterval = 500 + Math.random() * 1000; // 0.5-1.5秒随机移动间隔
                this.color = '#e74c3c';
            }

            getRandomDirection() {
                const directions = ['up', 'right', 'down', 'left'];
                return directions[Math.floor(Math.random() * directions.length)];
            }

            draw() {
                ctx.save();
                ctx.translate(this.x + this.width / 2, this.y + this.height / 2);
                
                // 根据方向旋转坦克
                switch (this.direction) {
                    case 'up':
                        ctx.rotate(0);
                        break;
                    case 'right':
                        ctx.rotate(Math.PI / 2);
                        break;
                    case 'down':
                        ctx.rotate(Math.PI);
                        break;
                    case 'left':
                        ctx.rotate(-Math.PI / 2);
                        break;
                }
                
                // 绘制坦克主体
                ctx.fillStyle = this.color;
                ctx.fillRect(-this.width / 2, -this.height / 2, this.width, this.height);
                
                // 绘制坦克炮管
                ctx.fillStyle = '#c0392b';
                ctx.fillRect(0, -this.width / 8, this.width / 2, this.width / 4);
                
                // 绘制坦克细节
                ctx.fillStyle = '#922b21';
                ctx.fillRect(-this.width / 4, -this.height / 4, this.width / 2, this.height / 2);
                
                ctx.restore();
            }

            update(deltaTime) {
                this.moveTimer += deltaTime;
                this.shootCooldown += deltaTime;
                
                // 移动逻辑
                if (this.moveTimer >= this.moveInterval) {
                    this.moveTimer = 0;
                    this.moveInterval = 500 + Math.random() * 1000;
                    
                    // 随机决定是否改变方向
                    if (Math.random() < 0.3) {
                        this.direction = this.getRandomDirection();
                    }
                }
                
                // 根据方向移动
                let newX = this.x;
                let newY = this.y;
                
                switch (this.direction) {
                    case 'up':
                        newY -= this.speed;
                        break;
                    case 'right':
                        newX += this.speed;
                        break;
                    case 'down':
                        newY += this.speed;
                        break;
                    case 'left':
                        newX -= this.speed;
                        break;
                }
                
                // 边界检查和碰撞检测
                if (newX >= 0 && newX <= canvas.width - this.width &&
                    newY >= 0 && newY <= canvas.height - this.height) {
                    
                    // 简单的碰撞检测
                    let canMove = true;
                    const testTank = { x: newX, y: newY, width: this.width, height: this.height };
                    
                    // 检查与墙壁的碰撞
                    for (const wall of gameState.walls) {
                        if (wall.active && this.intersectsRect(testTank, wall)) {
                            canMove = false;
                            break;
                        }
                    }
                    
                    // 检查与其他敌人的碰撞
                    for (const enemy of gameState.enemies) {
                        if (enemy !== this && enemy.active && this.intersectsRect(testTank, enemy)) {
                            canMove = false;
                            break;
                        }
                    }
                    
                    if (canMove) {
                        this.x = newX;
                        this.y = newY;
                    } else {
                        // 如果不能移动，改变方向
                        this.direction = this.getRandomDirection();
                    }
                } else {
                    // 如果碰到边界，改变方向
                    this.direction = this.getRandomDirection();
                }
                
                // 射击逻辑
                if (this.shootCooldown >= this.shootInterval) {
                    this.shoot();
                    this.shootCooldown = 0;
                    this.shootInterval = 1000 + Math.random() * 2000;
                }
            }
            
            intersectsRect(rect1, rect2) {
                return rect1.x < rect2.x + rect2.width &&
                       rect1.x + rect1.width > rect2.x &&
                       rect1.y < rect2.y + rect2.height &&
                       rect1.y + rect1.height > rect2.y;
            }
            
            shoot() {
                let bulletX = this.x + this.width / 2;
                let bulletY = this.y + this.height / 2;
                
                switch (this.direction) {
                    case 'up':
                        bulletY -= this.height / 2;
                        break;
                    case 'right':
                        bulletX += this.width / 2;
                        break;
                    case 'down':
                        bulletY += this.height / 2;
                        break;
                    case 'left':
                        bulletX -= this.width / 2;
                        break;
                }
                
                gameState.bullets.push(new Bullet(bulletX, bulletY, this.direction, 'enemy'));
            }
        }

        // 子弹类
        class Bullet extends GameObject {
            constructor(x, y, direction, owner) {
                super(x, y, GAME_CONFIG.bulletSize, GAME_CONFIG.bulletSize);
                this.direction = direction;
                this.owner = owner; // 'player' 或 'enemy'
                this.speed = owner === 'player' ? GAME_CONFIG.bulletSpeed : GAME_CONFIG.enemyBulletSpeed;
                this.color = owner === 'player' ? '#f1c40f' : '#e67e22';
            }

            draw() {
                ctx.fillStyle = this.color;
                ctx.fillRect(this.x, this.y, this.width, this.height);
            }

            update(deltaTime) {
                switch (this.direction) {
                    case 'up':
                        this.y -= this.speed;
                        break;
                    case 'right':
                        this.x += this.speed;
                        break;
                    case 'down':
                        this.y += this.speed;
                        break;
                    case 'left':
                        this.x -= this.speed;
                        break;
                }
                
                // 检查是否超出边界
                if (this.x < 0 || this.x > canvas.width || 
                    this.y < 0 || this.y > canvas.height) {
                    this.active = false;
                }
            }
        }

        // 墙壁类
        class Wall extends GameObject {
            constructor(x, y, type = 'brick') {
                super(x, y, GAME_CONFIG.tileSize, GAME_CONFIG.tileSize);
                this.type = type; // 'brick' 或 'steel'
                this.health = type === 'brick' ? GAME_CONFIG.wallHealth.brick : GAME_CONFIG.wallHealth.steel;
                this.maxHealth = this.health;
                this.color = type === 'brick' ? '#d35400' : '#7f8