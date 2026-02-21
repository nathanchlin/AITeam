# UI界面与得分系统实现

**Agent**: coder

**Time**: 2026-02-19T18:06:13.230127

---

我将为你实现一个完整的坦克大战游戏，包含UI界面和得分系统。以下是完整的单文件HTML代码：

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
            background-color: #2c3e50;
            font-family: 'Arial', sans-serif;
            color: white;
        }
        
        #gameContainer {
            position: relative;
            background-color: #34495e;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.5);
            padding: 20px;
        }
        
        #gameCanvas {
            border: 2px solid #ecf0f1;
            background-color: #1a252f;
            display: block;
        }
        
        #gameUI {
            position: absolute;
            top: 30px;
            left: 30px;
            right: 30px;
            display: flex;
            justify-content: space-between;
            pointer-events: none;
        }
        
        .playerInfo {
            background-color: rgba(0, 0, 0, 0.7);
            padding: 10px 15px;
            border-radius: 8px;
            min-width: 150px;
        }
        
        .playerName {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .healthBar {
            width: 100%;
            height: 10px;
            background-color: #555;
            border-radius: 5px;
            margin: 5px 0;
            overflow: hidden;
        }
        
        .healthFill {
            height: 100%;
            background-color: #2ecc71;
            transition: width 0.3s ease;
        }
        
        .score {
            font-size: 16px;
            margin-top: 5px;
        }
        
        #gameInstructions {
            position: absolute;
            bottom: 30px;
            left: 30px;
            right: 30px;
            background-color: rgba(0, 0, 0, 0.7);
            padding: 15px;
            border-radius: 8px;
            font-size: 14px;
            line-height: 1.5;
        }
        
        .controls {
            display: flex;
            justify-content: space-between;
        }
        
        .playerControls {
            flex: 1;
        }
        
        #gameMessage {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background-color: rgba(0, 0, 0, 0.9);
            padding: 30px;
            border-radius: 10px;
            text-align: center;
            display: none;
            z-index: 10;
        }
        
        #gameMessage h2 {
            margin-top: 0;
            font-size: 32px;
            color: #f39c12;
        }
        
        #gameMessage p {
            margin: 15px 0;
            font-size: 18px;
        }
        
        #restartButton {
            background-color: #3498db;
            color: white;
            border: none;
            padding: 10px 20px;
            font-size: 16px;
            border-radius: 5px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        
        #restartButton:hover {
            background-color: #2980b9;
        }
    </style>
</head>
<body>
    <div id="gameContainer">
        <canvas id="gameCanvas" width="800" height="600"></canvas>
        
        <div id="gameUI">
            <div class="playerInfo">
                <div class="playerName">玩家1</div>
                <div class="healthBar">
                    <div class="healthFill" id="player1Health" style="width: 100%"></div>
                </div>
                <div class="score">得分: <span id="player1Score">0</span></div>
            </div>
            
            <div class="playerInfo">
                <div class="playerName">玩家2</div>
                <div class="healthBar">
                    <div class="healthFill" id="player2Health" style="width: 100%"></div>
                </div>
                <div class="score">得分: <span id="player2Score">0</span></div>
            </div>
        </div>
        
        <div id="gameInstructions">
            <div class="controls">
                <div class="playerControls">
                    <strong>玩家1控制:</strong> WASD移动, 空格键射击
                </div>
                <div class="playerControls">
                    <strong>玩家2控制:</strong> 方向键移动, 回车键射击
                </div>
            </div>
        </div>
        
        <div id="gameMessage">
            <h2 id="messageTitle">游戏结束</h2>
            <p id="messageText"></p>
            <button id="restartButton">重新开始</button>
        </div>
    </div>

    <script>
        // 游戏配置
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const TILE_SIZE = 40;
        const GRID_WIDTH = canvas.width / TILE_SIZE;
        const GRID_HEIGHT = canvas.height / TILE_SIZE;
        
        // 游戏状态
        let gameRunning = true;
        let animationId = null;
        
        // 玩家数据
        const players = {
            player1: {
                x: 1,
                y: 1,
                direction: 'right',
                health: 100,
                maxHealth: 100,
                score: 0,
                color: '#3498db',
                keys: {
                    up: 'w',
                    down: 's',
                    left: 'a',
                    right: 'd',
                    shoot: ' '
                }
            },
            player2: {
                x: GRID_WIDTH - 2,
                y: GRID_HEIGHT - 2,
                direction: 'left',
                health: 100,
                maxHealth: 100,
                score: 0,
                color: '#e74c3c',
                keys: {
                    up: 'ArrowUp',
                    down: 'ArrowDown',
                    left: 'ArrowLeft',
                    right: 'ArrowRight',
                    shoot: 'Enter'
                }
            }
        };
        
        // 子弹数组
        const bullets = [];
        
        // 爆炸效果数组
        const explosions = [];
        
        // 障碍物地图 (0: 空地, 1: 墙壁)
        const map = [
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,1],
            [1,0,1,1,0,0,0,0,0,1,1,0,0,0,0,1,1,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,1,1,0,0,0,0,0,0,1,1,0,0,0,0,1],
            [1,0,0,0,0,1,1,0,0,0,0,0,0,1,1,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,1],
            [1,0,1,1,0,0,0,0,0,1,1,0,0,0,0,1,1,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,1,1,0,0,1,1,0,0,1,1,0,0,0,0,1],
            [1,0,0,0,0,1,1,0,0,0,0,0,0,1,1,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
        ];
        
        // 按键状态
        const keys = {};
        
        // 键盘事件监听
        window.addEventListener('keydown', (e) => {
            keys[e.key] = true;
            
            // 防止方向键和空格键滚动页面
            if(['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', ' '].includes(e.key)) {
                e.preventDefault();
            }
        });
        
        window.addEventListener('keyup', (e) => {
            keys[e.key] = false;
        });
        
        // 重新开始按钮
        document.getElementById('restartButton').addEventListener('click', restartGame);
        
        // 游戏主循环
        function gameLoop() {
            if (!gameRunning) return;
            
            update();
            render();
            
            animationId = requestAnimationFrame(gameLoop);
        }
        
        // 更新游戏状态
        function update() {
            // 更新玩家1
            updatePlayer(players.player1);
            
            // 更新玩家2
            updatePlayer(players.player2);
            
            // 更新子弹
            updateBullets();
            
            // 更新爆炸效果
            updateExplosions();
            
            // 检查游戏胜利条件
            checkWinCondition();
        }
        
        // 更新玩家状态
        function updatePlayer(player) {
            let moved = false;
            let newDirection = player.direction;
            
            // 移动控制
            if (keys[player.keys.up] && player.y > 0 && map[player.y - 1][player.x] === 0) {
                player.y--;
                newDirection = 'up';
                moved = true;
            } else if (keys[player.keys.down] && player.y < GRID_HEIGHT - 1 && map[player.y + 1][player.x] === 0) {
                player.y++;
                newDirection = 'down';
                moved = true;
            } else if (keys[player.keys.left] && player.x > 0 && map[player.y][player.x - 1] === 0) {
                player.x--;
                newDirection = 'left';
                moved = true;
            } else if (keys[player.keys.right] && player.x < GRID_WIDTH - 1 && map[player.y][player.x + 1] === 0) {
                player.x++;
                newDirection = 'right';
                moved = true;
            }
            
            // 更新方向
            if (moved) {
                player.direction = newDirection;
            }
            
            // 射击控制
            if (keys[player.keys.shoot] && !player.shootCooldown) {
                shoot(player);
                player.shootCooldown = true;
                setTimeout(() => {
                    player.shootCooldown = false;
                }, 300);
            }
        }
        
        // 发射子弹
        function shoot(player) {
            let bulletX = player.x;
            let bulletY = player.y;
            let bulletDirection = player.direction;
            
            // 根据方向调整子弹初始位置
            switch (bulletDirection) {
                case 'up':
                    bulletY -= 1;
                    break;
                case 'down':
                    bulletY += 1;
                    break;
                case 'left':
                    bulletX -= 1;
                    break;
                case 'right':
                    bulletX += 1;
                    break;
            }
            
            // 创建子弹
            bullets.push({
                x: bulletX,
                y: bulletY,
                direction: bulletDirection,
                speed: 0.2,
                owner: player === players.player1 ? 'player1' : 'player2',
                color: player.color
            });
        }
        
        // 更新子弹位置
        function updateBullets() {
            for (let i = bullets.length - 1; i >= 0; i--) {
                const bullet = bullets[i];
                
                // 移动子弹
                switch (bullet.direction) {
                    case 'up':
                        bullet.y -= bullet.speed;
                        break;
                    case 'down':
                        bullet.y += bullet.speed;
                        break;
                    case 'left':
                        bullet.x -= bullet.speed;
                        break;
                    case 'right':
                        bullet.x += bullet.speed;
                        break;
                }
                
                // 检查子弹是否出界
                if (bullet.x < 0 || bullet.x >= GRID_WIDTH || bullet.y < 0 || bullet.y >= GRID_HEIGHT) {
                    bullets.splice(i, 1);
                    continue;
                }
                
                // 检查子弹是否击中墙壁
                if (map[Math.floor(bullet.y)][Math.floor(bullet.x)] === 1) {
                    createExplosion(bullet.x, bullet.y);
                    bullets.splice(i, 1);
                    continue;
                }
                
                // 检查子弹是否击中玩家
                for (const [playerId, player] of Object.entries(players)) {
                    if (playerId !== bullet.owner && 
                        Math.abs(bullet.x - player.x) < 0.5 && 
                        Math.abs(bullet.y - player.y) < 0.5) {
                        
                        // 造成伤害
                        player.health -= 20;
                        
                        // 更新UI
                        updateHealthUI(playerId, player.health);
                        
                        // 创建爆炸效果
                        createExplosion(player.x, player.y);
                        
                        // 移除子弹
                        bullets.splice(i, 1);
                        
                        // 检查玩家是否死亡
                        if (player.health <= 0) {
                            player.health = 0;
                            endGame(playerId === 'player1' ? 'player2' : 'player1');
                        }
                        
                        break;
                    }
                }
            }
        }
        
        // 创建爆炸效果
        function createExplosion(x, y) {
            explosions.push({
                x: x,
                y: y,
                radius: 0,
                maxRadius: 1.5,
                speed: 0.1,
                color: '#f39c12'
            });
            
            // 增加射击玩家的得分
            for (const [playerId, player] of Object.entries(players)) {
                if (Math.abs(player.x - x) < 1 && Math.abs(player.y - y) < 1) {
                    player.score += 10;
                    updateScoreUI(playerId, player.score);
                }
            }
        }
        
        // 更新爆炸效果
        function updateExplosions() {
            for (let i = explosions.length - 1; i >= 0; i--) {
                const explosion = explosions[i];
                
                // 扩大爆炸范围
                explosion.radius += explosion.speed;
                
                // 移除完成的爆炸
                if (explosion.radius >= explosion.maxRadius) {
                    explosions.splice(i, 1);
                }
            }
        }
        
        // 渲染游戏画面
        function render() {
            // 清空画布
            ctx.fillStyle = '#1a252f';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            // 绘制地图
            drawMap();
            
            // 绘制玩家
            drawPlayer(players.player1);
            drawPlayer(players.player2);
            
            // 绘制子弹
            drawBullets();
            
            // 绘制爆炸效果
            drawExplosions();
        }
        
        // 绘制地图
        function drawMap() {
            for (let y = 0; y < GRID_HEIGHT; y++) {
                for (let x = 0; x < GRID_WIDTH; x++) {
                    if (map[y][x] === 1) {
                        ctx.fillStyle = '#7f8c8d';
                        ctx.fillRect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE);
                        
                        // 添加墙壁纹理
                        ctx.strokeStyle = '#95a5a6';
                        ctx.lineWidth = 2;
                        ctx.strokeRect(x * TILE_SIZE + 2, y * TILE_SIZE + 2, TILE_SIZE - 4, TILE_SIZE - 4);
                    }
                }
            }
        }
        
        // 绘