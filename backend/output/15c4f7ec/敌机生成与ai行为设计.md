# 敌机生成与AI行为设计

**Agent**: coder

**Time**: 2026-02-19T20:49:45.452006

---

# 敌机生成与AI行为设计

我将为1942风格的打飞机游戏设计敌机生成机制和AI行为逻辑，包括不同类型敌机的移动模式和AI行为。这将是一个完整的单文件HTML实现，整合了之前的功能并添加了敌机系统。

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>1942 打飞机游戏</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            background-color: #111;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            font-family: Arial, sans-serif;
            overflow: hidden;
        }
        
        #gameContainer {
            position: relative;
            width: 800px;
            height: 600px;
            box-shadow: 0 0 20px rgba(0, 255, 255, 0.5);
        }
        
        canvas {
            background-color: #000;
            border: 2px solid #0ff;
            display: block;
        }
        
        #gameInfo {
            position: absolute;
            top: 10px;
            left: 10px;
            color: #0ff;
            font-size: 16px;
            text-shadow: 0 0 5px rgba(0, 255, 255, 0.8);
        }
        
        #gameOver {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            color: #f00;
            font-size: 48px;
            text-align: center;
            display: none;
            text-shadow: 0 0 10px rgba(255, 0, 0, 0.8);
        }
        
        #startScreen {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            color: #0ff;
            font-size: 24px;
            text-align: center;
        }
        
        button {
            background-color: transparent;
            border: 2px solid #0ff;
            color: #0ff;
            padding: 10px 20px;
            font-size: 18px;
            cursor: pointer;
            margin-top: 20px;
            transition: all 0.3s;
        }
        
        button:hover {
            background-color: #0ff;
            color: #000;
            box-shadow: 0 0 10px rgba(0, 255, 255, 0.8);
        }
    </style>
</head>
<body>
    <div id="gameContainer">
        <canvas id="gameCanvas" width="800" height="600"></canvas>
        <div id="gameInfo">
            <div>分数: <span id="score">0</span></div>
            <div>生命: <span id="lives">3</span></div>
        </div>
        <div id="gameOver">
            <div>游戏结束</div>
            <div>最终分数: <span id="finalScore">0</span></div>
            <button onclick="game.restart()">重新开始</button>
        </div>
        <div id="startScreen">
            <h1>1942 打飞机游戏</h1>
            <p>使用方向键移动飞机，空格键射击</p>
            <button onclick="game.start()">开始游戏</button>
        </div>
    </div>

    <script>
        // 游戏状态枚举
        const GameState = {
            MENU: 'menu',
            PLAYING: 'playing',
            PAUSED: 'paused',
            GAME_OVER: 'game_over'
        };

        // 敌机类型枚举
        const EnemyType = {
            BASIC: 'basic',
            FAST: 'fast',
            HEAVY: 'heavy',
            BOSS: 'boss'
        };

        // 游戏主类
        class Game {
            constructor() {
                this.canvas = document.getElementById('gameCanvas');
                this.ctx = this.canvas.getContext('2d');
                this.state = GameState.MENU;
                this.score = 0;
                this.lives = 3;
                this.level = 1;
                this.keys = {};
                this.player = null;
                this.bullets = [];
                this.enemies = [];
                this.enemyBullets = [];
                this.particles = [];
                this.enemySpawnTimer = 0;
                this.enemySpawnInterval = 120; // 初始生成间隔（帧数）
                this.backgroundY = 0;
                
                // 绑定事件
                this.bindEvents();
            }

            bindEvents() {
                // 键盘事件
                window.addEventListener('keydown', (e) => {
                    this.keys[e.key] = true;
                    
                    // 防止空格键滚动页面
                    if (e.key === ' ') {
                        e.preventDefault();
                    }
                });
                
                window.addEventListener('keyup', (e) => {
                    this.keys[e.key] = false;
                });
            }

            start() {
                this.state = GameState.PLAYING;
                document.getElementById('startScreen').style.display = 'none';
                document.getElementById('gameOver').style.display = 'none';
                
                // 初始化玩家
                this.player = new Player(400, 500);
                
                // 重置游戏数据
                this.score = 0;
                this.lives = 3;
                this.level = 1;
                this.bullets = [];
                this.enemies = [];
                this.enemyBullets = [];
                this.particles = [];
                this.enemySpawnTimer = 0;
                this.enemySpawnInterval = 120;
                
                // 更新UI
                this.updateUI();
                
                // 开始游戏循环
                this.gameLoop();
            }

            restart() {
                this.start();
            }

            gameLoop() {
                if (this.state === GameState.PLAYING) {
                    this.update();
                    this.render();
                }
                
                requestAnimationFrame(() => this.gameLoop());
            }

            update() {
                // 更新背景
                this.updateBackground();
                
                // 更新玩家
                if (this.player) {
                    this.player.update(this.keys);
                    
                    // 玩家射击
                    if (this.keys[' '] && this.player.canShoot()) {
                        this.bullets.push(new Bullet(this.player.x, this.player.y - 20, -8, true));
                        this.player.shoot();
                    }
                }
                
                // 生成敌机
                this.spawnEnemies();
                
                // 更新子弹
                this.updateBullets();
                
                // 更新敌机
                this.updateEnemies();
                
                // 更新粒子效果
                this.updateParticles();
                
                // 检测碰撞
                this.checkCollisions();
                
                // 更新UI
                this.updateUI();
            }

            updateBackground() {
                // 滚动背景
                this.backgroundY += 1;
                if (this.backgroundY >= this.canvas.height) {
                    this.backgroundY = 0;
                }
            }

            spawnEnemies() {
                this.enemySpawnTimer++;
                
                // 根据等级调整生成间隔
                const adjustedInterval = Math.max(30, this.enemySpawnInterval - this.level * 5);
                
                if (this.enemySpawnTimer >= adjustedInterval) {
                    this.enemySpawnTimer = 0;
                    
                    // 根据游戏进度决定敌机类型
                    let enemyType = EnemyType.BASIC;
                    const rand = Math.random();
                    
                    if (this.level >= 3 && rand < 0.1) {
                        enemyType = EnemyType.BOSS;
                    } else if (this.level >= 2 && rand < 0.3) {
                        enemyType = EnemyType.HEAVY;
                    } else if (rand < 0.6) {
                        enemyType = EnemyType.FAST;
                    }
                    
                    // 随机生成位置
                    const x = Math.random() * (this.canvas.width - 40) + 20;
                    
                    // 创建敌机
                    this.enemies.push(new Enemy(x, -30, enemyType));
                }
            }

            updateBullets() {
                // 更新玩家子弹
                for (let i = this.bullets.length - 1; i >= 0; i--) {
                    const bullet = this.bullets[i];
                    bullet.update();
                    
                    // 移除超出屏幕的子弹
                    if (bullet.y < -10 || bullet.y > this.canvas.height + 10) {
                        this.bullets.splice(i, 1);
                    }
                }
                
                // 更新敌机子弹
                for (let i = this.enemyBullets.length - 1; i >= 0; i--) {
                    const bullet = this.enemyBullets[i];
                    bullet.update();
                    
                    // 移除超出屏幕的子弹
                    if (bullet.y < -10 || bullet.y > this.canvas.height + 10) {
                        this.enemyBullets.splice(i, 1);
                    }
                }
            }

            updateEnemies() {
                for (let i = this.enemies.length - 1; i >= 0; i--) {
                    const enemy = this.enemies[i];
                    enemy.update();
                    
                    // 敌机射击
                    if (enemy.canShoot()) {
                        this.enemyBullets.push(new Bullet(enemy.x, enemy.y + 20, 4, false));
                        enemy.shoot();
                    }
                    
                    // 移除超出屏幕的敌机
                    if (enemy.y > this.canvas.height + 30) {
                        this.enemies.splice(i, 1);
                    }
                }
            }

            updateParticles() {
                for (let i = this.particles.length - 1; i >= 0; i--) {
                    const particle = this.particles[i];
                    particle.update();
                    
                    // 移除已经消失的粒子
                    if (particle.life <= 0) {
                        this.particles.splice(i, 1);
                    }
                }
            }

            checkCollisions() {
                // 玩家子弹与敌机碰撞
                for (let i = this.bullets.length - 1; i >= 0; i--) {
                    const bullet = this.bullets[i];
                    
                    for (let j = this.enemies.length - 1; j >= 0; j--) {
                        const enemy = this.enemies[j];
                        
                        if (this.checkCollision(bullet, enemy)) {
                            // 创建爆炸效果
                            this.createExplosion(enemy.x, enemy.y);
                            
                            // 根据敌机类型增加分数
                            this.score += enemy.points;
                            
                            // 减少敌机生命值
                            enemy.hit();
                            
                            // 如果敌机被摧毁
                            if (enemy.health <= 0) {
                                this.enemies.splice(j, 1);
                                
                                // 检查是否是Boss
                                if (enemy.type === EnemyType.BOSS) {
                                    this.level++;
                                    this.enemySpawnInterval = Math.max(30, this.enemySpawnInterval - 10);
                                }
                            }
                            
                            // 移除子弹
                            this.bullets.splice(i, 1);
                            break;
                        }
                    }
                }
                
                // 敌机子弹与玩家碰撞
                if (this.player) {
                    for (let i = this.enemyBullets.length - 1; i >= 0; i--) {
                        const bullet = this.enemyBullets[i];
                        
                        if (this.checkCollision(bullet, this.player)) {
                            // 创建爆炸效果
                            this.createExplosion(this.player.x, this.player.y);
                            
                            // 减少玩家生命值
                            this.lives--;
                            
                            // 移除子弹
                            this.enemyBullets.splice(i, 1);
                            
                            // 检查游戏是否结束
                            if (this.lives <= 0) {
                                this.gameOver();
                            }
                            break;
                        }
                    }
                }
                
                // 敌机与玩家碰撞
                if (this.player) {
                    for (let i = this.enemies.length - 1; i >= 0; i--) {
                        const enemy = this.enemies[i];
                        
                        if (this.checkCollision(enemy, this.player)) {
                            // 创建爆炸效果
                            this.createExplosion(enemy.x, enemy.y);
                            this.createExplosion(this.player.x, this.player.y);
                            
                            // 减少双方生命值
                            this.lives--;
                            enemy.hit();
                            
                            // 如果敌机被摧毁
                            if (enemy.health <= 0) {
                                this.enemies.splice(i, 1);
                                this.score += enemy.points;
                                
                                // 检查是否是Boss
                                if (enemy.type === EnemyType.BOSS) {
                                    this.level++;
                                    this.enemySpawnInterval = Math.max(30, this.enemySpawnInterval - 10);
                                }
                            }
                            
                            // 检查游戏是否结束
                            if (this.lives <= 0) {
                                this.gameOver();
                            }
                            break;
                        }
                    }
                }
            }

            checkCollision(obj1, obj2) {
                const distance = Math.sqrt(
                    Math.pow(obj1.x - obj2.x, 2) + 
                    Math.pow(obj1.y - obj2.y, 2)
                );
                
                return distance < (obj1.radius + obj2.radius);
            }

            createExplosion(x, y) {
                // 创建多个粒子模拟爆炸效果
                for (let i = 0; i < 15; i++) {
                    const angle = Math.random() * Math.PI * 2;
                    const speed = Math.random() * 3 + 1;
                    const vx = Math.cos(angle) * speed;
                    const vy = Math.sin(angle) * speed;
                    
                    this.particles.push(new Particle(x, y, vx, vy));
                }
            }

            gameOver() {
                this.state = GameState.GAME_OVER;
                document.getElementById('finalScore').textContent = this.score;
                document.getElementById('gameOver').style.display = 'block';
            }

            updateUI() {
                document.getElementById('score').textContent = this.score;
                document.getElementById('lives').textContent = this.lives;
            }

            render() {
                // 清空画布
                this.ctx.fillStyle = '#000';
                this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
                
                // 绘制背景
                this.renderBackground();
                
                // 绘制玩家
                if (this.player) {
                    this.player.render(this.ctx);
                }
                
                // 绘制敌机
                this.enemies.forEach(enemy => enemy.render(this.ctx));
                
                // 绘制子弹
                this.bullets.forEach(bullet => bullet.render(this.ctx));
                this.enemyBullets.forEach(bullet => bullet.render(this.ctx));
                
                // 绘制粒子效果
                this.particles.forEach(particle => particle.render(this.ctx));
            }

            renderBackground() {
                // 绘制星空背景
                this.ctx.fillStyle = '#fff';
                
                // 绘制静态星星
                for (let i = 0; i < 50; i++) {
                    const x = (i * 37) % this.canvas.width;
                    const y = (i * 23 + this.backgroundY) % this.canvas.height;
                    const size = (i % 3) + 1;
                    
                    this.ctx.beginPath();
                    this.ctx.arc(x, y, size, 0, Math.PI * 2);
                    this.ctx.fill();
                }
            }
        }

        // 玩家类
        class Player {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.radius = 15;
                this.speed = 5;
                this.shootCooldown = 0;
                this.shootRate = 10; // 射击间隔（帧数）
            }

            update(keys) {
                // 移动控制
                if (keys['ArrowLeft'] && this.x > this.radius) {
                    this.x -= this.speed;
                }
                if (keys['ArrowRight'] && this.x < game.canvas.width - this.radius) {
                    this.x += this.speed;
                }
                if (keys['ArrowUp'] && this.y > this.radius) {
                    this.y -= this.speed;
                }
                if (keys['ArrowDown'] && this.y < game.canvas.height - this.radius) {
                    this.y += this.speed;
                }
                
                // 更新射击冷却
                if (this.shootCooldown > 0) {
                    this.shootCooldown--;
                }
            }

            canShoot() {
                return this.shootCooldown <= 0;
            }

            shoot() {
                this.shootCooldown = this.shootRate;
            }

            render(ctx) {
                // 绘制玩家飞机
                ctx.fillStyle = '#0ff';
                
                // 机身
                ctx.beginPath();
                ctx.moveTo(this.x, this.y - 15);
                ctx.lineTo(this.x - 10, this.y + 10);
                ctx.lineTo(this.x, this.y + 5);
                ctx.lineTo(this.x + 10, this.y + 10);
                ctx.closePath();
                ctx.fill();
                
                // 机翼
                ctx.fillRect(this.x - 20, this.y, 40, 5);
                
                // 引擎火焰
                ctx.fillStyle = '#f80';
                ctx.beginPath();
                ctx.moveTo(this.x - 5, this.y + 5);
                ctx.lineTo(this.x, this.y + 15);
                ctx.lineTo(this.x + 5, this.y + 5);
                ctx.closePath();
                ctx.fill();
            }
        }

        // 敌机类
        class Enemy {
            constructor(x, y, type) {
                this.x = x;
                this.y = y;
                this.type = type;
                this.shootCooldown = 0;
                this.shootRate = 80; // 初始射击间隔
                
                // 根据类型设置属性
                switch (type) {
                    case EnemyType.BASIC:
                        this.radius = 12;
                        this.speed = 2;
                        this.health = 1;
                        this.points = 10;
                        this.color = '#f00';
                        this.shootRate = 100;
                        break;
                    case EnemyType.FAST:
                        this.radius = 10;
                        this.speed = 4;
                        this.health = 1;
                        this.points = 20;
                        this.color = '#f0f';
                        this.shootRate = 60;
                        break;
                    case EnemyType.HEAVY:
                        this.radius = 18;
                        this.speed = 1.5;
                        this.health = 3;
                        this.points = 50;
                        this.color = '#ff0';
                        this.shootRate = 120;
                        break;
                    case EnemyType.BOSS:
                        this.radius = 30;
                        this.speed = 1;
                        this.health = 10;
                        this.points = 200;
                        this.color = '#f00';
                        this.shootRate = 40;
                        break;
                }
                
                // AI行为参数