# 实现敌方坦克AI系统

**Agent**: coder

**Time**: 2026-02-17T20:49:27.842732

---

我将为您实现一个完整的坦克大战游戏，包含敌方AI系统。以下是完整的HTML文件代码：

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
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background-color: #111;
            font-family: 'Courier New', monospace;
            color: #fff;
        }
        
        .game-container {
            position: relative;
            width: 800px;
            height: 600px;
            background-color: #000;
            border: 2px solid #0f0;
            box-shadow: 0 0 20px #0f0;
        }
        
        canvas {
            display: block;
            image-rendering: pixelated;
            image-rendering: -moz-crisp-edges;
            image-rendering: crisp-edges;
        }
        
        .score {
            position: absolute;
            top: 10px;
            left: 10px;
            font-size: 20px;
            color: #0f0;
            text-shadow: 0 0 5px #0f0;
        }
        
        .game-over {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 40px;
            color: #f00;
            text-align: center;
            display: none;
            text-shadow: 0 0 10px #f00;
        }
        
        .restart-btn {
            margin-top: 20px;
            padding: 10px 20px;
            font-size: 20px;
            background-color: #0f0;
            color: #000;
            border: none;
            cursor: pointer;
            font-family: 'Courier New', monospace;
            font-weight: bold;
            transition: all 0.3s;
        }
        
        .restart-btn:hover {
            background-color: #0a0;
            box-shadow: 0 0 10px #0f0;
        }
        
        .controls {
            position: absolute;
            bottom: 10px;
            right: 10px;
            font-size: 14px;
            color: #0f0;
            text-align: right;
            opacity: 0.7;
        }
    </style>
</head>
<body>
    <div class="game-container">
        <canvas id="gameCanvas" width="800" height="600"></canvas>
        <div class="score">得分: <span id="scoreValue">0</span></div>
        <div class="game-over" id="gameOver">
            游戏结束
            <br>
            <button class="restart-btn" onclick="restartGame()">重新开始</button>
        </div>
        <div class="controls">
            WASD/方向键: 移动坦克<br>
            空格键: 射击
        </div>
    </div>

    <script>
        // 获取画布和上下文
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        ctx.imageSmoothingEnabled = false;
        
        // 游戏常量
        const TILE_SIZE = 20;
        const GAME_WIDTH = canvas.width;
        const GAME_HEIGHT = canvas.height;
        const TANK_SPEED = 2;
        const BULLET_SPEED = 5;
        const ENEMY_BULLET_SPEED = 3;
        const ENEMY_SHOOT_COOLDOWN = 2000; // 毫秒
        const ENEMY_MOVE_COOLDOWN = 1000; // 毫秒
        
        // 游戏状态
        let gameState = 'playing'; // 'playing', 'paused', 'gameOver'
        let score = 0;
        let lastTime = 0;
        
        // 游戏对象
        let playerTank;
        let enemyTanks = [];
        let bullets = [];
        let walls = [];
        
        // 键盘状态
        const keys = {};
        
        // 坦克类
        class Tank {
            constructor(x, y, color, isPlayer = false) {
                this.x = x;
                this.y = y;
                this.width = TILE_SIZE;
                this.height = TILE_SIZE;
                this.color = color;
                this.direction = 'up'; // 'up', 'down', 'left', 'right'
                this.isPlayer = isPlayer;
                this.speed = TANK_SPEED;
                this.lastShotTime = 0;
                this.shootCooldown = isPlayer ? 500 : ENEMY_SHOOT_COOLDOWN;
                this.health = isPlayer ? 1 : 1;
            }
            
            draw() {
                ctx.fillStyle = this.color;
                
                // 绘制坦克主体
                ctx.fillRect(this.x, this.y, this.width, this.height);
                
                // 绘制坦克炮管
                ctx.fillStyle = '#000';
                switch(this.direction) {
                    case 'up':
                        ctx.fillRect(this.x + this.width/2 - 2, this.y - 5, 4, 10);
                        break;
                    case 'down':
                        ctx.fillRect(this.x + this.width/2 - 2, this.y + this.height - 5, 4, 10);
                        break;
                    case 'left':
                        ctx.fillRect(this.x - 5, this.y + this.height/2 - 2, 10, 4);
                        break;
                    case 'right':
                        ctx.fillRect(this.x + this.width - 5, this.y + this.height/2 - 2, 10, 4);
                        break;
                }
                
                // 绘制坦克细节
                ctx.fillStyle = this.isPlayer ? '#0ff' : '#f00';
                ctx.fillRect(this.x + 4, this.y + 4, this.width - 8, this.height - 8);
            }
            
            move(direction) {
                this.direction = direction;
                let newX = this.x;
                let newY = this.y;
                
                switch(direction) {
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
                if (newX >= 0 && newX + this.width <= GAME_WIDTH && 
                    newY >= 0 && newY + this.height <= GAME_HEIGHT) {
                    
                    // 碰撞检测
                    let canMove = true;
                    for (let wall of walls) {
                        if (this.checkCollision(newX, newY, this.width, this.height, wall.x, wall.y, wall.width, wall.height)) {
                            canMove = false;
                            break;
                        }
                    }
                    
                    // 坦克之间的碰撞检测
                    for (let tank of [...enemyTanks, playerTank]) {
                        if (tank !== this && this.checkCollision(newX, newY, this.width, this.height, tank.x, tank.y, tank.width, tank.height)) {
                            canMove = false;
                            break;
                        }
                    }
                    
                    if (canMove) {
                        this.x = newX;
                        this.y = newY;
                    }
                }
            }
            
            shoot() {
                const now = Date.now();
                if (now - this.lastShotTime < this.shootCooldown) {
                    return;
                }
                
                this.lastShotTime = now;
                let bulletX = this.x + this.width/2 - 2;
                let bulletY = this.y + this.height/2 - 2;
                
                bullets.push(new Bullet(bulletX, bulletY, this.direction, this.isPlayer ? 'player' : 'enemy'));
            }
            
            checkCollision(x1, y1, w1, h1, x2, y2, w2, h2) {
                return x1 < x2 + w2 && x1 + w1 > x2 && y1 < y2 + h2 && y1 + h1 > y2;
            }
        }
        
        // 子弹类
        class Bullet {
            constructor(x, y, direction, owner) {
                this.x = x;
                this.y = y;
                this.width = 4;
                this.height = 4;
                this.direction = direction;
                this.owner = owner; // 'player' or 'enemy'
                this.speed = owner === 'player' ? BULLET_SPEED : ENEMY_BULLET_SPEED;
                this.active = true;
            }
            
            draw() {
                ctx.fillStyle = this.owner === 'player' ? '#0ff' : '#f00';
                ctx.fillRect(this.x, this.y, this.width, this.height);
            }
            
            move() {
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
                
                // 检查是否超出边界
                if (this.x < 0 || this.x + this.width > GAME_WIDTH || 
                    this.y < 0 || this.y + this.height > GAME_HEIGHT) {
                    this.active = false;
                }
            }
            
            checkCollision(target) {
                return this.x < target.x + target.width && 
                       this.x + this.width > target.x && 
                       this.y < target.y + target.height && 
                       this.y + this.height > target.y;
            }
        }
        
        // 墙壁类
        class Wall {
            constructor(x, y, destructible = true) {
                this.x = x;
                this.y = y;
                this.width = TILE_SIZE;
                this.height = TILE_SIZE;
                this.destructible = destructible;
                this.health = destructible ? 1 : Infinity;
            }
            
            draw() {
                ctx.fillStyle = this.destructible ? '#8B4513' : '#555';
                ctx.fillRect(this.x, this.y, this.width, this.height);
                
                // 绘制砖块纹理
                if (this.destructible) {
                    ctx.strokeStyle = '#654321';
                    ctx.lineWidth = 1;
                    ctx.beginPath();
                    ctx.moveTo(this.x + this.width/2, this.y);
                    ctx.lineTo(this.x + this.width/2, this.y + this.height);
                    ctx.moveTo(this.x, this.y + this.height/2);
                    ctx.lineTo(this.x + this.width, this.y + this.height/2);
                    ctx.stroke();
                }
            }
            
            hit() {
                if (this.destructible) {
                    this.health--;
                    return this.health <= 0;
                }
                return false;
            }
        }
        
        // 初始化游戏
        function initGame() {
            // 创建玩家坦克
            playerTank = new Tank(400, 500, '#0f0', true);
            
            // 创建敌方坦克
            enemyTanks = [];
            enemyTanks.push(new Tank(100, 100, '#f00', false));
            enemyTanks.push(new Tank(700, 100, '#f00', false));
            enemyTanks.push(new Tank(400, 50, '#f00', false));
            
            // 创建墙壁
            walls = [];
            // 创建边界墙
            for (let i = 0; i < GAME_WIDTH; i += TILE_SIZE) {
                walls.push(new Wall(i, 0, false)); // 上边界
                walls.push(new Wall(i, GAME_HEIGHT - TILE_SIZE, false)); // 下边界
            }
            for (let i = TILE_SIZE; i < GAME_HEIGHT - TILE_SIZE; i += TILE_SIZE) {
                walls.push(new Wall(0, i, false)); // 左边界
                walls.push(new Wall(GAME_WIDTH - TILE_SIZE, i, false)); // 右边界
            }
            
            // 创建一些随机可破坏的墙
            for (let i = 0; i < 30; i++) {
                let x, y;
                do {
                    x = Math.floor(Math.random() * (GAME_WIDTH / TILE_SIZE - 2)) * TILE_SIZE + TILE_SIZE;
                    y = Math.floor(Math.random() * (GAME_HEIGHT / TILE_SIZE - 2)) * TILE_SIZE + TILE_SIZE;
                } while (
                    // 确保不会在玩家坦克附近生成
                    (Math.abs(x - playerTank.x) < 3 * TILE_SIZE && Math.abs(y - playerTank.y) < 3 * TILE_SIZE) ||
                    // 确保不会在敌方坦克附近生成
                    enemyTanks.some(tank => Math.abs(x - tank.x) < 3 * TILE_SIZE && Math.abs(y - tank.y) < 3 * TILE_SIZE) ||
                    // 确保不会重叠
                    walls.some(wall => wall.x === x && wall.y === y)
                );
                
                walls.push(new Wall(x, y, true));
            }
            
            // 重置子弹
            bullets = [];
            
            // 重置得分
            score = 0;
            updateScore(0);
            
            // 重置游戏状态
            gameState = 'playing';
            document.getElementById('gameOver').style.display = 'none';
        }
        
        // 更新得分显示
        function updateScore(points) {
            score += points;
            document.getElementById('scoreValue').textContent = score;
        }
        
        // 处理玩家输入
        function handlePlayerInput() {
            if (gameState !== 'playing') return;
            
            // 移动
            if (keys['ArrowUp'] || keys['w'] || keys['W']) {
                playerTank.move('up');
            }
            if (keys['ArrowDown'] || keys['s'] || keys['S']) {
                playerTank.move('down');
            }
            if (keys['ArrowLeft'] || keys['a'] || keys['A']) {
                playerTank.move('left');
            }
            if (keys['ArrowRight'] || keys['d'] || keys['D']) {
                playerTank.move('right');
            }
            
            // 射击
            if (keys[' ']) {
                playerTank.shoot();
            }
        }
        
        // 敌方AI逻辑
        function moveEnemyTanks() {
            if (gameState !== 'playing') return;
            
            const now = Date.now();
            
            enemyTanks.forEach(tank => {
                // 随机移动
                if (Math.random() < 0.02 || now - tank.lastMoveTime > ENEMY_MOVE_COOLDOWN) {
                    const directions = ['up', 'down', 'left', 'right'];
                    const randomDirection = directions[Math.floor(Math.random() * directions.length)];
                    tank.move(randomDirection);
                    tank.lastMoveTime = now;
                }
                
                // 随机射击
                if (Math.random() < 0.01 || now - tank.lastShotTime > ENEMY_SHOOT_COOLDOWN) {
                    tank.shoot();
                    tank.lastShotTime = now;
                }
            });
        }
        
        // 移动子弹
        function moveBullets() {
            bullets = bullets.filter(bullet => {
                if (!bullet.active) return false;
                
                bullet.move();
                
                // 检查与墙壁的碰撞
                for (let i = 0; i < walls.length; i++) {
                    if (bullet.checkCollision(walls[i])) {
                        if (walls[i].hit()) {
                            walls.splice(i, 1);
                            updateScore(10); // 摧毁墙壁得分
                        }
                        bullet.active = false;
                        return false;
                    }
                }
                
                // 检查与坦克的碰撞
                if (bullet.owner === 'player') {
                    for (let i = 0; i < enemyTanks.length; i++) {
                        if (bullet.checkCollision(enemyTanks[i])) {
                            enemyTanks.splice(i, 1);
                            updateScore(100); // 击毁敌方坦克得分
                            bullet.active = false;
                            return false;
                        }
                    }
                } else {
                    if (bullet.checkCollision(playerTank)) {
                        gameState = 'gameOver';
                        document.getElementById('gameOver').style.display = 'block';
                        bullet.active = false;
                        return false;
                    }
                }
                
                return bullet.active;
            });
        }
        
        // 检查坦克与墙壁的碰撞
        function checkTankWallCollisions() {
            // 这个功能已经在Tank类的move方法中实现了
        }
        
        // 游戏主循环
        function gameLoop(currentTime) {
            const deltaTime = currentTime - lastTime;
            lastTime = currentTime;
            
            // 清空画布
            ctx.fillStyle = '#000';
            ctx.fillRect(0, 0, GAME_WIDTH, GAME_HEIGHT);
            
            // 处理输入
            handlePlayerInput();
            
            // 更新游戏状态
            moveEnemyTanks();
            moveBullets();
            
            // 绘制游戏对象
            walls.forEach(wall => wall.draw());
            enemyTanks.forEach(tank => tank.draw());
            playerTank.draw();
            bullets.forEach(bullet => bullet.draw());
            
            // 检查游戏结束条件
            if (enemyTanks.length === 0 && gameState === 'playing') {
                gameState = 'gameOver';
                document.getElementById('gameOver').innerHTML = 
                    '恭喜胜利！<br>得分: ' + score + 
                    '<br><button class="restart-btn" onclick="restartGame()">重新开始</button>';
                document.getElementById('gameOver').style.display = 'block';
            }
            
            requestAnimationFrame(gameLoop);
        }
        
        // 重新开始游戏
        function restartGame() {
            initGame();
        }
        
        // 键盘事件监听
        window.addEventListener('keydown', (e) => {
            keys[e.key] = true;
            
            // 防止空格键滚动页面
            if (e.key === ' ') {
                e.preventDefault();
            }
        });
        
        window.addEventListener('keyup', (e) => {
            keys[e.key] = false;
        });
        
        // 初始化并启动游戏
        initGame();
        requestAnimationFrame(gameLoop);
    </script>
</body>
</html>
```

这个完整的坦克大战游戏实现了以下功能：

1. **玩家控制**：
   - 使用WASD或方向键控制坦克移动
   - 空格键发射子弹
   - 坦克有射击冷却时间

2. **敌方AI系统**：
   - 3个敌方坦克自动移动
   - 随机改变方向移动
   - 随机射击子弹
   - 有移动和射击的冷却时间

3. **游戏机制**：
   - 砖墙障碍物可以被子弹摧毁