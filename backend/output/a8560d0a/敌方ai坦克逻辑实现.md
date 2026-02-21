# 敌方AI坦克逻辑实现

**Agent**: coder

**Time**: 2026-02-18T16:06:11.045070

---

我来为您实现一个完整的坦克大战游戏，包含敌方AI坦克的自动移动、寻路和攻击逻辑。

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>坦克大战 - 敌方AI坦克实现</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            background-color: #2c3e50;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            font-family: Arial, sans-serif;
        }
        
        #gameContainer {
            text-align: center;
        }
        
        canvas {
            border: 2px solid #34495e;
            background-color: #1a252f;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.5);
        }
        
        #gameInfo {
            color: #ecf0f1;
            margin-top: 10px;
            font-size: 16px;
        }
        
        #gameOver {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background-color: rgba(0, 0, 0, 0.8);
            color: #ecf0f1;
            padding: 20px 40px;
            border-radius: 10px;
            font-size: 24px;
            display: none;
        }
    </style>
</head>
<body>
    <div id="gameContainer">
        <canvas id="gameCanvas" width="800" height="600"></canvas>
        <div id="gameInfo">
            <div>生命值: <span id="playerHealth">100</span> | 得分: <span id="score">0</span></div>
            <div>使用方向键移动，空格键射击</div>
        </div>
        <div id="gameOver"></div>
    </div>

    <script>
        // 游戏配置
        const GAME_CONFIG = {
            CANVAS_WIDTH: 800,
            CANVAS_HEIGHT: 600,
            TANK_SIZE: 30,
            BULLET_SIZE: 5,
            BULLET_SPEED: 8,
            TANK_SPEED: 2,
            AI_UPDATE_INTERVAL: 500, // AI更新间隔(毫秒)
            MAX_ENEMY_TANKS: 5,
            ENEMY_SPAWN_INTERVAL: 3000 // 敌人生成间隔(毫秒)
        };

        // 游戏状态
        const game = {
            canvas: null,
            ctx: null,
            player: null,
            enemies: [],
            bullets: [],
            playerBullets: [],
            enemyBullets: [],
            walls: [],
            playerBase: null,
            enemyBase: null,
            score: 0,
            gameOver: false,
            lastAIUpdate: 0,
            lastEnemySpawn: 0
        };

        // 坦克类
        class Tank {
            constructor(x, y, color, isPlayer = false) {
                this.x = x;
                this.y = y;
                this.width = GAME_CONFIG.TANK_SIZE;
                this.height = GAME_CONFIG.TANK_SIZE;
                this.color = color;
                this.direction = 0; // 0: 上, 1: 右, 2: 下, 3: 左
                this.speed = GAME_CONFIG.TANK_SPEED;
                this.isPlayer = isPlayer;
                this.health = 100;
                this.lastShot = 0;
                this.shotCooldown = isPlayer ? 500 : 1000; // 玩家射击冷却500ms，敌人1000ms
                this.targetX = null;
                this.targetY = null;
                this.path = [];
                this.lastDirectionChange = 0;
                this.directionChangeInterval = 1000; // AI方向改变间隔
            }

            update() {
                if (this.isPlayer) {
                    // 玩家坦克由键盘控制
                    this.handlePlayerMovement();
                } else {
                    // AI坦克自动移动
                    this.handleAIMovement();
                }

                // 边界检查
                this.x = Math.max(this.width / 2, Math.min(game.canvas.width - this.width / 2, this.x));
                this.y = Math.max(this.height / 2, Math.min(game.canvas.height - this.height / 2, this.y));
            }

            handlePlayerMovement() {
                // 玩家移动逻辑在键盘事件中处理
            }

            handleAIMovement() {
                const now = Date.now();
                
                // 如果没有目标或已经到达目标，设置新目标
                if (!this.targetX || this.reachedTarget() || now - this.lastDirectionChange > this.directionChangeInterval) {
                    this.setNewTarget();
                    this.lastDirectionChange = now;
                }
                
                // 向目标移动
                if (this.targetX && this.targetY) {
                    this.moveTowardsTarget();
                }
                
                // 随机射击
                if (now - this.lastShot > this.shotCooldown && Math.random() < 0.02) {
                    this.shoot();
                    this.lastShot = now;
                }
            }

            setNewTarget() {
                // 设置目标为玩家基地或随机位置
                if (Math.random() < 0.7) {
                    // 70%概率向玩家基地移动
                    this.targetX = game.playerBase.x;
                    this.targetY = game.playerBase.y;
                } else {
                    // 30%概率随机移动
                    this.targetX = Math.random() * (game.canvas.width - 100) + 50;
                    this.targetY = Math.random() * (game.canvas.height - 100) + 50;
                }
                
                // 简单的路径规划：直接朝目标移动
                this.path = [{x: this.targetX, y: this.targetY}];
            }

            moveTowardsTarget() {
                if (!this.path || this.path.length === 0) return;
                
                const target = this.path[0];
                const dx = target.x - this.x;
                const dy = target.y - this.y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                
                if (distance < 5) {
                    // 到达目标点
                    this.path.shift();
                    if (this.path.length === 0) {
                        this.targetX = null;
                        this.targetY = null;
                    }
                    return;
                }
                
                // 计算移动方向
                let newDirection = this.direction;
                
                if (Math.abs(dx) > Math.abs(dy)) {
                    // 水平移动
                    newDirection = dx > 0 ? 1 : 3; // 右或左
                } else {
                    // 垂直移动
                    newDirection = dy > 0 ? 2 : 0; // 下或上
                }
                
                // 如果方向改变，更新方向
                if (newDirection !== this.direction) {
                    this.direction = newDirection;
                }
                
                // 根据方向移动
                switch (this.direction) {
                    case 0: // 上
                        this.y -= this.speed;
                        break;
                    case 1: // 右
                        this.x += this.speed;
                        break;
                    case 2: // 下
                        this.y += this.speed;
                        break;
                    case 3: // 左
                        this.x -= this.speed;
                        break;
                }
                
                // 碰撞检测
                if (this.checkWallCollision()) {
                    // 如果碰撞墙壁，回退并改变方向
                    this.goBack();
                    this.setNewTarget();
                }
            }

            reachedTarget() {
                if (!this.targetX || !this.targetY) return true;
                
                const dx = this.targetX - this.x;
                const dy = this.targetY - this.y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                
                return distance < 10;
            }

            goBack() {
                switch (this.direction) {
                    case 0: // 上
                        this.y += this.speed;
                        break;
                    case 1: // 右
                        this.x -= this.speed;
                        break;
                    case 2: // 下
                        this.y -= this.speed;
                        break;
                    case 3: // 左
                        this.x += this.speed;
                        break;
                }
            }

            checkWallCollision() {
                for (const wall of game.walls) {
                    if (this.x < wall.x + wall.width &&
                        this.x + this.width > wall.x &&
                        this.y < wall.y + wall.height &&
                        this.y + this.height > wall.y) {
                        return true;
                    }
                }
                return false;
            }

            shoot() {
                const now = Date.now();
                if (now - this.lastShot < this.shotCooldown) return;
                
                const bullet = new Bullet(
                    this.x,
                    this.y,
                    this.direction,
                    this.isPlayer,
                    this.isPlayer ? 'player' : 'enemy'
                );
                
                if (this.isPlayer) {
                    game.playerBullets.push(bullet);
                } else {
                    game.enemyBullets.push(bullet);
                }
                
                this.lastShot = now;
            }

            draw(ctx) {
                ctx.save();
                ctx.translate(this.x, this.y);
                ctx.rotate(this.direction * Math.PI / 2);
                
                // 绘制坦克主体
                ctx.fillStyle = this.color;
                ctx.fillRect(-this.width / 2, -this.height / 2, this.width, this.height);
                
                // 绘制坦克炮管
                ctx.fillStyle = this.isPlayer ? '#3498db' : '#e74c3c';
                ctx.fillRect(0, -3, this.width / 2, 6);
                
                // 绘制坦克细节
                ctx.fillStyle = '#2c3e50';
                ctx.fillRect(-5, -5, 10, 10);
                
                ctx.restore();
                
                // 绘制血条
                if (!this.isPlayer) {
                    ctx.fillStyle = 'red';
                    ctx.fillRect(this.x - 15, this.y - 25, 30, 4);
                    ctx.fillStyle = 'green';
                    ctx.fillRect(this.x - 15, this.y - 25, 30 * (this.health / 100), 4);
                }
            }

            takeDamage(damage) {
                this.health -= damage;
                if (this.health <= 0) {
                    return true; // 坦克被摧毁
                }
                return false;
            }
        }

        // 子弹类
        class Bullet {
            constructor(x, y, direction, isPlayer, owner) {
                this.x = x;
                this.y = y;
                this.width = GAME_CONFIG.BULLET_SIZE;
                this.height = GAME_CONFIG.BULLET_SIZE;
                this.direction = direction;
                this.speed = GAME_CONFIG.BULLET_SPEED;
                this.isPlayer = isPlayer;
                this.owner = owner;
            }

            update() {
                switch (this.direction) {
                    case 0: // 上
                        this.y -= this.speed;
                        break;
                    case 1: // 右
                        this.x += this.speed;
                        break;
                    case 2: // 下
                        this.y += this.speed;
                        break;
                    case 3: // 左
                        this.x -= this.speed;
                        break;
                }
            }

            draw(ctx) {
                ctx.fillStyle = this.isPlayer ? '#3498db' : '#e74c3c';
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.width / 2, 0, Math.PI * 2);
                ctx.fill();
            }

            isOutOfBounds() {
                return this.x < 0 || this.x > game.canvas.width ||
                       this.y < 0 || this.y > game.canvas.height;
            }
        }

        // 墙壁类
        class Wall {
            constructor(x, y, width, height) {
                this.x = x;
                this.y = y;
                this.width = width;
                this.height = height;
            }

            draw(ctx) {
                ctx.fillStyle = '#7f8c8d';
                ctx.fillRect(this.x, this.y, this.width, this.height);
                
                // 添加砖块纹理
                ctx.strokeStyle = '#95a5a6';
                ctx.lineWidth = 1;
                
                for (let i = 0; i < this.width; i += 20) {
                    for (let j = 0; j < this.height; j += 20) {
                        ctx.strokeRect(this.x + i, this.y + j, 20, 20);
                    }
                }
            }
        }

        // 基地类
        class Base {
            constructor(x, y, isPlayer) {
                this.x = x;
                this.y = y;
                this.width = 40;
                this.height = 40;
                this.isPlayer = isPlayer;
                this.health = 100;
            }

            draw(ctx) {
                ctx.fillStyle = this.isPlayer ? '#2ecc71' : '#e74c3c';
                ctx.fillRect(this.x - this.width / 2, this.y - this.height / 2, this.width, this.height);
                
                // 绘制基地标志
                ctx.fillStyle = '#ecf0f1';
                ctx.font = 'bold 20px Arial';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText(this.isPlayer ? 'P' : 'E', this.x, this.y);
                
                // 绘制血条
                ctx.fillStyle = 'red';
                ctx.fillRect(this.x - 20, this.y - 30, 40, 4);
                ctx.fillStyle = 'green';
                ctx.fillRect(this.x - 20, this.y - 30, 40 * (this.health / 100), 4);
            }

            takeDamage(damage) {
                this.health -= damage;
                if (this.health <= 0) {
                    return true; // 基地被摧毁
                }
                return false;
            }
        }

        // 初始化游戏
        function initGame() {
            game.canvas = document.getElementById('gameCanvas');
            game.ctx = game.canvas.getContext('2d');
            
            // 创建玩家坦克
            game.player = new Tank(
                game.canvas.width / 2,
                game.canvas.height - 50,
                '#3498db',
                true
            );
            
            // 创建基地
            game.playerBase = new Base(
                game.canvas.width / 2,
                game.canvas.height - 20,
                true
            );
            
            game.enemyBase = new Base(
                game.canvas.width / 2,
                20,
                false
            );
            
            // 创建墙壁
            createWalls();
            
            // 绑定键盘事件
            bindKeyboardEvents();
            
            // 开始游戏循环
            gameLoop();
        }

        // 创建墙壁
        function createWalls() {
            // 创建边界墙
            game.walls.push(new Wall(0, 0, game.canvas.width, 10)); // 上边界
            game.walls.push(new Wall(0, game.canvas.height - 10, game.canvas.width, 10)); // 下边界
            game.walls.push(new Wall(0, 0, 10, game.canvas.height)); // 左边界
            game.walls.push(new Wall(game.canvas.width - 10, 0, 10, game.canvas.height)); // 右边界
            
            // 创建中间障碍墙
            game.walls.push(new Wall(200, 150, 100, 20));
            game.walls.push(new Wall(500, 150, 100, 20));
            game.walls.push(new Wall(200, 300, 20, 100));
            game.walls.push(new Wall(580, 300, 20, 100));
            game.walls.push(new Wall(350, 400, 100, 20));
        }

        // 绑定键盘事件
        function bindKeyboardEvents() {
            const keys = {};
            
            document.addEventListener('keydown', (e) => {
                keys[e.key] = true;
                
                if (e.key === ' ' && !game.gameOver) {
                    e.preventDefault();
                    game.player.shoot();
                }
            });
            
            document.addEventListener('keyup', (e) => {
                keys[e.key] = false;
            });
            
            // 更新玩家移动
            setInterval(() => {
                if (game.gameOver) return;
                
                let dx = 0;
                let dy = 0;
                
                if (keys['ArrowUp']) dy = -1;
                if (keys['ArrowDown']) dy = 1;
                if (keys['ArrowLeft']) dx = -1;
                if (keys['ArrowRight']) dx = 1;
                
                // 归一化对角线移动
                if (dx !== 0 && dy !== 0) {
                    dx *= 0.707;
                    dy *= 0.707;
                }
                
                // 更新玩家方向
                if (dx > 0) game.player.direction = 1;
                else if (dx < 0) game.player.direction = 3;
                else if (dy > 0) game.player.direction = 2;
                else if (dy < 0) game.player.direction = 0;
                
                // 移动玩家
                const oldX = game.player.x;
                const oldY = game.player.y;
                
                game.player.x += dx * game.player.speed;
                game.player.y += dy * game.player.speed;
                
                // 检查墙壁碰撞
                if (game.player.checkWallCollision()) {
                    game.player.x = oldX;
                    game.player.y = oldY;
                }
            }, 16);
        }

        // 生成敌人坦克
        function spawnEnemy() {
            if (game.enemies.length >= GAME_CONFIG.MAX_ENEMY_TANKS) return;
            
            // 随机在顶部生成敌人
            const x = Math.random() * (game.canvas.width - 100) + 50;
            const enemy = new Tank(x, 50, '#e74c3c', false);
            game.enemies.push(enemy);
        }

        // 更新游戏状态
        function updateGame() {
            if (game.gameOver) return;
            
            const now = Date.now();
            
            // 生成敌人
            if (now - game.lastEnemySpawn > GAME_CONFIG.ENEMY_SPAWN_INTERVAL) {
                spawnEnemy();
                game.lastEnemySpawn = now;
            }
            
            // 更新玩家
            game.player.update();
            
            // 更新敌人
            game.enemies.forEach((enemy, index) => {
                enemy.update();
                
                // 检查敌人是否到达玩家基地
                const dx = enemy.x - game.playerBase.x;
                const dy = enemy.y - game.playerBase.y;
                const distance =