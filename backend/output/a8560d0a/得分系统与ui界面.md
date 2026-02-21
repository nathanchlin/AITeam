# 得分系统与UI界面

**Agent**: coder

**Time**: 2026-02-18T16:09:51.376710

---

我将为您创建一个完整的坦克大战游戏，包含得分系统和UI界面。这个单文件HTML游戏将包含所有必要的功能。

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>坦克大战</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            background-color: #111;
            font-family: 'Arial', sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            overflow: hidden;
        }
        
        #gameContainer {
            position: relative;
            border: 3px solid #0f0;
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.5);
        }
        
        #gameCanvas {
            display: block;
            background-color: #000;
        }
        
        #gameUI {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
        }
        
        .ui-element {
            position: absolute;
            color: #0f0;
            font-size: 18px;
            font-weight: bold;
            text-shadow: 0 0 5px rgba(0, 255, 0, 0.8);
        }
        
        #score {
            top: 10px;
            left: 10px;
        }
        
        #lives {
            top: 10px;
            right: 10px;
        }
        
        #level {
            top: 40px;
            left: 10px;
        }
        
        #gameStatus {
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 36px;
            text-align: center;
            display: none;
        }
        
        #gameOver {
            background-color: rgba(0, 0, 0, 0.8);
            padding: 20px;
            border-radius: 10px;
            border: 2px solid #f00;
        }
        
        #gameOver h2 {
            color: #f00;
            margin-top: 0;
        }
        
        #gameOver button {
            background-color: #0f0;
            color: #000;
            border: none;
            padding: 10px 20px;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            margin-top: 10px;
            pointer-events: auto;
        }
        
        #gameOver button:hover {
            background-color: #0a0;
        }
        
        #controls {
            position: absolute;
            bottom: 10px;
            left: 50%;
            transform: translateX(-50%);
            color: #0f0;
            font-size: 14px;
            text-align: center;
        }
    </style>
</head>
<body>
    <div id="gameContainer">
        <canvas id="gameCanvas" width="800" height="600"></canvas>
        <div id="gameUI">
            <div id="score" class="ui-element">得分: 0</div>
            <div id="lives" class="ui-element">生命: 3</div>
            <div id="level" class="ui-element">关卡: 1</div>
            <div id="gameStatus">
                <div id="gameOver">
                    <h2 id="gameOverTitle">游戏结束</h2>
                    <p id="finalScore">最终得分: 0</p>
                    <button id="restartBtn">重新开始</button>
                </div>
            </div>
            <div id="controls">
                使用方向键移动坦克 | 空格键发射子弹
            </div>
        </div>
    </div>

    <script>
        // 游戏配置
        const GAME_CONFIG = {
            CANVAS_WIDTH: 800,
            CANVAS_HEIGHT: 600,
            TANK_SIZE: 30,
            BULLET_SIZE: 5,
            BULLET_SPEED: 8,
            ENEMY_BULLET_SPEED: 5,
            ENEMY_SPEED: 2,
            ENEMY_SPAWN_RATE: 100, // 帧数
            BASE_SIZE: 40,
            MAX_ENEMIES: 5
        };

        // 游戏状态
        let gameState = {
            score: 0,
            lives: 3,
            level: 1,
            gameRunning: true,
            frameCount: 0,
            keys: {},
            playerBullets: [],
            enemyBullets: [],
            enemies: [],
            particles: []
        };

        // 获取画布和上下文
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');

        // 玩家坦克类
        class PlayerTank {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.width = GAME_CONFIG.TANK_SIZE;
                this.height = GAME_CONFIG.TANK_SIZE;
                this.speed = 4;
                this.direction = 'up';
                this.color = '#0f0';
                this.lastShot = 0;
                this.shotCooldown = 15; // 帧数
            }

            update() {
                // 处理移动
                if (gameState.keys['ArrowUp'] && this.y > 0) {
                    this.y -= this.speed;
                    this.direction = 'up';
                }
                if (gameState.keys['ArrowDown'] && this.y < canvas.height - this.height) {
                    this.y += this.speed;
                    this.direction = 'down';
                }
                if (gameState.keys['ArrowLeft'] && this.x > 0) {
                    this.x -= this.speed;
                    this.direction = 'left';
                }
                if (gameState.keys['ArrowRight'] && this.x < canvas.width - this.width) {
                    this.x += this.speed;
                    this.direction = 'right';
                }

                // 处理射击
                if (gameState.keys[' '] && gameState.frameCount - this.lastShot > this.shotCooldown) {
                    this.shoot();
                    this.lastShot = gameState.frameCount;
                }
            }

            shoot() {
                let bulletX = this.x + this.width / 2;
                let bulletY = this.y + this.height / 2;
                
                switch(this.direction) {
                    case 'up':
                        bulletY -= this.height / 2;
                        break;
                    case 'down':
                        bulletY += this.height / 2;
                        break;
                    case 'left':
                        bulletX -= this.width / 2;
                        break;
                    case 'right':
                        bulletX += this.width / 2;
                        break;
                }
                
                gameState.playerBullets.push(new Bullet(bulletX, bulletY, this.direction, '#0f0', GAME_CONFIG.BULLET_SPEED));
            }

            draw() {
                ctx.save();
                ctx.fillStyle = this.color;
                
                // 绘制坦克主体
                ctx.fillRect(this.x, this.y, this.width, this.height);
                
                // 绘制炮管
                ctx.fillStyle = '#0a0';
                let barrelLength = this.width * 0.8;
                let barrelWidth = this.width * 0.2;
                
                switch(this.direction) {
                    case 'up':
                        ctx.fillRect(this.x + (this.width - barrelWidth) / 2, this.y - barrelLength / 2, barrelWidth, barrelLength);
                        break;
                    case 'down':
                        ctx.fillRect(this.x + (this.width - barrelWidth) / 2, this.y + this.height - barrelLength / 2, barrelWidth, barrelLength);
                        break;
                    case 'left':
                        ctx.fillRect(this.x - barrelLength / 2, this.y + (this.height - barrelWidth) / 2, barrelLength, barrelWidth);
                        break;
                    case 'right':
                        ctx.fillRect(this.x + this.width - barrelLength / 2, this.y + (this.height - barrelWidth) / 2, barrelLength, barrelWidth);
                        break;
                }
                
                // 绘制坦克细节
                ctx.fillStyle = '#0f0';
                ctx.fillRect(this.x + this.width * 0.3, this.y + this.height * 0.3, this.width * 0.4, this.height * 0.4);
                
                ctx.restore();
            }
        }

        // 敌人坦克类
        class EnemyTank {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.width = GAME_CONFIG.TANK_SIZE;
                this.height = GAME_CONFIG.TANK_SIZE;
                this.speed = GAME_CONFIG.ENEMY_SPEED;
                this.direction = this.getRandomDirection();
                this.color = '#f00';
                this.lastShot = 0;
                this.shotCooldown = 100 + Math.random() * 100; // 随机射击间隔
                this.moveTimer = 0;
                this.moveInterval = 60 + Math.random() * 60; // 随机移动间隔
            }

            getRandomDirection() {
                const directions = ['up', 'down', 'left', 'right'];
                return directions[Math.floor(Math.random() * directions.length)];
            }

            update() {
                this.moveTimer++;
                
                // 定期改变方向
                if (this.moveTimer >= this.moveInterval) {
                    this.direction = this.getRandomDirection();
                    this.moveTimer = 0;
                    this.moveInterval = 60 + Math.random() * 60;
                }
                
                // 移动
                let newX = this.x;
                let newY = this.y;
                
                switch(this.direction) {
                    case 'up':
                        newY -= this.speed;
                        break;
                    case 'down':
                        newY += this.speed;
                        break;
                    case 'left':
                        newX -= this.speed;
                        break;
                    case 'right':
                        newX += this.speed;
                        break;
                }
                
                // 边界检查
                if (newX >= 0 && newX <= canvas.width - this.width && 
                    newY >= 0 && newY <= canvas.height - this.height) {
                    this.x = newX;
                    this.y = newY;
                } else {
                    // 碰到边界，改变方向
                    this.direction = this.getRandomDirection();
                }
                
                // 射击
                if (gameState.frameCount - this.lastShot > this.shotCooldown) {
                    this.shoot();
                    this.lastShot = gameState.frameCount;
                    this.shotCooldown = 100 + Math.random() * 100;
                }
            }

            shoot() {
                let bulletX = this.x + this.width / 2;
                let bulletY = this.y + this.height / 2;
                
                gameState.enemyBullets.push(new Bullet(bulletX, bulletY, this.direction, '#f00', GAME_CONFIG.ENEMY_BULLET_SPEED));
            }

            draw() {
                ctx.save();
                ctx.fillStyle = this.color;
                
                // 绘制坦克主体
                ctx.fillRect(this.x, this.y, this.width, this.height);
                
                // 绘制炮管
                ctx.fillStyle = '#a00';
                let barrelLength = this.width * 0.8;
                let barrelWidth = this.width * 0.2;
                
                switch(this.direction) {
                    case 'up':
                        ctx.fillRect(this.x + (this.width - barrelWidth) / 2, this.y - barrelLength / 2, barrelWidth, barrelLength);
                        break;
                    case 'down':
                        ctx.fillRect(this.x + (this.width - barrelWidth) / 2, this.y + this.height - barrelLength / 2, barrelWidth, barrelLength);
                        break;
                    case 'left':
                        ctx.fillRect(this.x - barrelLength / 2, this.y + (this.height - barrelWidth) / 2, barrelLength, barrelWidth);
                        break;
                    case 'right':
                        ctx.fillRect(this.x + this.width - barrelLength / 2, this.y + (this.height - barrelWidth) / 2, barrelLength, barrelWidth);
                        break;
                }
                
                // 绘制坦克细节
                ctx.fillStyle = '#f00';
                ctx.fillRect(this.x + this.width * 0.3, this.y + this.height * 0.3, this.width * 0.4, this.height * 0.4);
                
                ctx.restore();
            }
        }

        // 子弹类
        class Bullet {
            constructor(x, y, direction, color, speed) {
                this.x = x;
                this.y = y;
                this.direction = direction;
                this.color = color;
                this.speed = speed;
                this.width = GAME_CONFIG.BULLET_SIZE;
                this.height = GAME_CONFIG.BULLET_SIZE;
            }

            update() {
                switch(this.direction) {
                    case 'up':
                        this.y -= this.speed;
                        break;
                    case 'down':
                        this.y += this.speed;
                        break;
                    case 'left':
                        this.x -= this.speed;
                        break;
                    case 'right':
                        this.x += this.speed;
                        break;
                }
            }

            draw() {
                ctx.fillStyle = this.color;
                ctx.fillRect(this.x - this.width / 2, this.y - this.height / 2, this.width, this.height);
            }

            isOutOfBounds() {
                return this.x < 0 || this.x > canvas.width || 
                       this.y < 0 || this.y > canvas.height;
            }
        }

        // 粒子效果类
        class Particle {
            constructor(x, y, color) {
                this.x = x;
                this.y = y;
                this.vx = (Math.random() - 0.5) * 5;
                this.vy = (Math.random() - 0.5) * 5;
                this.color = color;
                this.life = 30;
                this.maxLife = 30;
            }

            update() {
                this.x += this.vx;
                this.y += this.vy;
                this.life--;
            }

            draw() {
                ctx.save();
                ctx.globalAlpha = this.life / this.maxLife;
                ctx.fillStyle = this.color;
                ctx.fillRect(this.x, this.y, 4, 4);
                ctx.restore();
            }
        }

        // 基地类
        class Base {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.width = GAME_CONFIG.BASE_SIZE;
                this.height = GAME_CONFIG.BASE_SIZE;
                this.color = '#00f';
                this.destroyed = false;
            }

            draw() {
                if (!this.destroyed) {
                    ctx.fillStyle = this.color;
                    ctx.fillRect(this.x, this.y, this.width, this.height);
                    
                    // 绘制基地标志
                    ctx.fillStyle = '#fff';
                    ctx.font = '20px Arial';
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.fillText('H', this.x + this.width / 2, this.y + this.height / 2);
                }
            }

            checkCollision(bullet) {
                if (!this.destroyed && 
                    bullet.x > this.x && bullet.x < this.x + this.width &&
                    bullet.y > this.y && bullet.y < this.y + this.height) {
                    this.destroyed = true;
                    return true;
                }
                return false;
            }
        }

        // 游戏对象
        let playerTank;
        let enemyBase;
        let playerBase;

        // 初始化游戏
        function initGame() {
            // 重置游戏状态
            gameState = {
                score: 0,
                lives: 3,
                level: 1,
                gameRunning: true,
                frameCount: 0,
                keys: {},
                playerBullets: [],
                enemyBullets: [],
                enemies: [],
                particles: []
            };
            
            // 创建玩家坦克
            playerTank = new PlayerTank(canvas.width / 2 - GAME_CONFIG.TANK_SIZE / 2, canvas.height - GAME_CONFIG.TANK_SIZE - 10);
            
            // 创建基地
            enemyBase = new Base(canvas.width / 2 - GAME_CONFIG.BASE_SIZE / 2, 10);
            playerBase = new Base(canvas.width / 2 - GAME_CONFIG.BASE_SIZE / 2, canvas.height - GAME_CONFIG.BASE_SIZE - 10);
            
            // 更新UI
            updateUI();
            
            // 隐藏游戏结束界面
            document.getElementById('gameStatus').style.display = 'none';
        }

        // 生成敌人
        function spawnEnemy() {
            if (gameState.enemies.length < GAME_CONFIG.MAX_ENEMIES && 
                gameState.frameCount % GAME_CONFIG.ENEMY_SPAWN_RATE === 0) {
                let x = Math.random() * (canvas.width - GAME_CONFIG.TANK_SIZE);
                gameState.enemies.push(new EnemyTank(x, 50));
            }
        }

        // 碰撞检测
        function checkCollisions() {
            // 玩家子弹与敌人碰撞
            for (let i = gameState.playerBullets.length - 1; i >= 0; i--) {
                let bullet = gameState.playerBullets[i];
                
                // 检查与敌人的碰撞
                for (let j = gameState.enemies.length - 1; j >= 0; j--) {
                    let enemy = gameState.enemies[j];
                    if (bullet.x > enemy.x && bullet.x < enemy.x + enemy.width &&
                        bullet.y > enemy.y && bullet.y < enemy.y + enemy.height) {
                        // 创建爆炸效果
                        createExplosion(enemy.x + enemy.width / 2, enemy.y + enemy.height / 2, '#f00');
                        
                        // 移除敌人和子弹
                        gameState.enemies.splice(j, 1);
                        gameState.playerBullets.splice(i, 1);
                        
                        // 增加分数
                        gameState.score += 100;
                        updateUI();
                        break;
                    }
                }
                
                // 检查与敌人基地的碰撞
                if (bullet && enemyBase && enemyBase.checkCollision(bullet)) {
                    createExplosion(enemyBase.x + enemyBase.width / 2, enemyBase.y + enemyBase.height / 2, '#00f');
                    gameState.playerBullets.splice(i, 1);
                    gameState.score += 500;
                    updateUI();
                    
                    // 检查是否通关
                    if (gameState.enemies.length === 0) {
                        nextLevel();
                    }
                }
            }
            
            // 敌人子弹与玩家碰撞
            for (let i = gameState.enemyBullets.length - 1; i >= 0; i--) {
                let bullet = gameState.enemyBullets[i];
                
                // 检查与玩家的碰撞
                if (bullet.x > playerTank.x && bullet.x < playerTank.x + playerTank.width &&
                    bullet.y > playerTank.y && bullet.y < playerTank.y + playerTank.height) {
                    createExplosion(playerTank.x + player