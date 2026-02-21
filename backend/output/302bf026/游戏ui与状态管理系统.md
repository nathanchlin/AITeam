# 游戏UI与状态管理系统

**Agent**: coder

**Time**: 2026-02-18T15:46:12.745603

---

我将为您开发一个完整的坦克大战游戏，包含UI系统、计分系统、生命值显示和关卡进度显示，以及游戏状态管理。以下是完整的单文件HTML代码：

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
            background-color: #2c3e50;
            font-family: 'Arial', sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            color: #ecf0f1;
        }
        
        .game-container {
            position: relative;
            background-color: #34495e;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.5);
            padding: 20px;
        }
        
        #gameCanvas {
            background-color: #1a252f;
            border: 2px solid #7f8c8d;
            border-radius: 5px;
            display: block;
        }
        
        .game-info {
            display: flex;
            justify-content: space-between;
            margin-bottom: 15px;
            padding: 10px;
            background-color: #2c3e50;
            border-radius: 5px;
        }
        
        .info-panel {
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        
        .info-label {
            font-size: 14px;
            color: #bdc3c7;
            margin-bottom: 5px;
        }
        
        .info-value {
            font-size: 20px;
            font-weight: bold;
            color: #3498db;
        }
        
        .life-bar {
            width: 150px;
            height: 20px;
            background-color: #7f8c8d;
            border-radius: 10px;
            overflow: hidden;
            margin-top: 5px;
        }
        
        .life-fill {
            height: 100%;
            background-color: #e74c3c;
            transition: width 0.3s ease;
        }
        
        .controls {
            margin-top: 15px;
            text-align: center;
        }
        
        button {
            background-color: #3498db;
            color: white;
            border: none;
            padding: 10px 20px;
            margin: 0 5px;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        
        button:hover {
            background-color: #2980b9;
        }
        
        button:disabled {
            background-color: #7f8c8d;
            cursor: not-allowed;
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
        }
        
        .game-over-text {
            font-size: 36px;
            margin-bottom: 20px;
        }
        
        .level-progress {
            width: 100%;
            height: 20px;
            background-color: #7f8c8d;
            border-radius: 10px;
            overflow: hidden;
            margin-top: 5px;
        }
        
        .level-fill {
            height: 100%;
            background-color: #2ecc71;
            transition: width 0.3s ease;
        }
    </style>
</head>
<body>
    <div class="game-container">
        <div class="game-info">
            <div class="info-panel">
                <div class="info-label">得分</div>
                <div class="info-value" id="score">0</div>
            </div>
            <div class="info-panel">
                <div class="info-label">生命值</div>
                <div class="life-bar">
                    <div class="life-fill" id="lifeFill" style="width: 100%;"></div>
                </div>
            </div>
            <div class="info-panel">
                <div class="info-label">关卡</div>
                <div class="info-value" id="level">1</div>
                <div class="level-progress">
                    <div class="level-fill" id="levelFill" style="width: 0%;"></div>
                </div>
            </div>
        </div>
        
        <canvas id="gameCanvas" width="800" height="600"></canvas>
        
        <div class="controls">
            <button id="startBtn">开始游戏</button>
            <button id="pauseBtn" disabled>暂停</button>
            <button id="restartBtn" disabled>重新开始</button>
        </div>
        
        <div class="game-over-overlay" id="gameOverOverlay">
            <div class="game-over-text" id="gameOverText">游戏结束</div>
            <div class="info-value" id="finalScore">最终得分: 0</div>
            <button id="playAgainBtn">再玩一次</button>
        </div>
    </div>

    <script>
        // 游戏状态常量
        const GameState = {
            MENU: 'menu',
            PLAYING: 'playing',
            PAUSED: 'paused',
            GAME_OVER: 'game_over'
        };

        // 游戏配置
        const GAME_CONFIG = {
            canvasWidth: 800,
            canvasHeight: 600,
            tankSpeed: 3,
            bulletSpeed: 5,
            enemyTankSpeed: 2,
            enemyFireRate: 2000, // 敌人坦克开火间隔（毫秒）
            enemySpawnRate: 3000, // 敌人生成间隔（毫秒）
            levelProgressRequirement: 10, // 每关需要消灭的敌人数量
            playerLives: 3,
            baseHealth: 100
        };

        // 游戏主类
        class TankGame {
            constructor() {
                this.canvas = document.getElementById('gameCanvas');
                this.ctx = this.canvas.getContext('2d');
                this.state = GameState.MENU;
                this.score = 0;
                this.level = 1;
                this.enemiesDestroyed = 0;
                this.lastTime = 0;
                this.gameLoopId = null;
                
                // 游戏对象
                this.playerTank = null;
                this.bullets = [];
                this.enemyTanks = [];
                this.enemyBullets = [];
                this.headquarters = null;
                
                // 计时器
                this.enemyFireTimer = 0;
                this.enemySpawnTimer = 0;
                
                // 按键状态
                this.keys = {};
                
                this.init();
            }
            
            init() {
                // 初始化游戏对象
                this.playerTank = new Tank(
                    GAME_CONFIG.canvasWidth / 2, 
                    GAME_CONFIG.canvasHeight - 100, 
                    'player'
                );
                
                this.headquarters = new Headquarters(
                    GAME_CONFIG.canvasWidth / 2 - 25, 
                    50, 
                    GAME_CONFIG.baseHealth
                );
                
                // 绑定事件
                this.bindEvents();
                
                // 更新UI
                this.updateUI();
            }
            
            bindEvents() {
                // 键盘事件
                window.addEventListener('keydown', (e) => {
                    this.keys[e.key] = true;
                    
                    // 空格键开火
                    if (e.key === ' ' && this.state === GameState.PLAYING) {
                        this.playerFire();
                    }
                });
                
                window.addEventListener('keyup', (e) => {
                    this.keys[e.key] = false;
                });
                
                // 按钮事件
                document.getElementById('startBtn').addEventListener('click', () => {
                    this.startGame();
                });
                
                document.getElementById('pauseBtn').addEventListener('click', () => {
                    this.togglePause();
                });
                
                document.getElementById('restartBtn').addEventListener('click', () => {
                    this.restartGame();
                });
                
                document.getElementById('playAgainBtn').addEventListener('click', () => {
                    this.restartGame();
                });
            }
            
            startGame() {
                this.state = GameState.PLAYING;
                document.getElementById('startBtn').disabled = true;
                document.getElementById('pauseBtn').disabled = false;
                document.getElementById('restartBtn').disabled = false;
                
                // 重置游戏对象
                this.playerTank.reset(
                    GAME_CONFIG.canvasWidth / 2, 
                    GAME_CONFIG.canvasHeight - 100
                );
                
                this.bullets = [];
                this.enemyTanks = [];
                this.enemyBullets = [];
                this.headquarters.reset();
                
                // 重置计时器
                this.enemyFireTimer = 0;
                this.enemySpawnTimer = 0;
                
                // 开始游戏循环
                this.gameLoop();
            }
            
            togglePause() {
                if (this.state === GameState.PLAYING) {
                    this.state = GameState.PAUSED;
                    document.getElementById('pauseBtn').textContent = '继续';
                    cancelAnimationFrame(this.gameLoopId);
                } else if (this.state === GameState.PAUSED) {
                    this.state = GameState.PLAYING;
                    document.getElementById('pauseBtn').textContent = '暂停';
                    this.gameLoop();
                }
            }
            
            restartGame() {
                // 重置游戏状态
                this.state = GameState.MENU;
                this.score = 0;
                this.level = 1;
                this.enemiesDestroyed = 0;
                
                // 重置UI
                document.getElementById('startBtn').disabled = false;
                document.getElementById('pauseBtn').disabled = true;
                document.getElementById('pauseBtn').textContent = '暂停';
                document.getElementById('restartBtn').disabled = true;
                document.getElementById('gameOverOverlay').style.display = 'none';
                
                // 重置游戏对象
                this.init();
                
                // 取消游戏循环
                if (this.gameLoopId) {
                    cancelAnimationFrame(this.gameLoopId);
                }
                
                // 清空画布
                this.ctx.clearRect(0, 0, GAME_CONFIG.canvasWidth, GAME_CONFIG.canvasHeight);
            }
            
            gameLoop(timestamp) {
                if (this.state !== GameState.PLAYING) return;
                
                const deltaTime = timestamp - this.lastTime;
                this.lastTime = timestamp;
                
                // 更新游戏状态
                this.update(deltaTime);
                
                // 渲染游戏
                this.render();
                
                // 继续游戏循环
                this.gameLoopId = requestAnimationFrame((t) => this.gameLoop(t));
            }
            
            update(deltaTime) {
                // 更新玩家坦克
                this.updatePlayerTank();
                
                // 更新子弹
                this.updateBullets();
                
                // 更新敌人坦克
                this.updateEnemyTanks(deltaTime);
                
                // 更新敌人子弹
                this.updateEnemyBullets();
                
                // 生成敌人
                this.spawnEnemies(deltaTime);
                
                // 检查游戏结束条件
                this.checkGameOver();
                
                // 检查关卡进度
                this.checkLevelProgress();
                
                // 更新UI
                this.updateUI();
            }
            
            updatePlayerTank() {
                // 处理玩家移动
                if (this.keys['ArrowUp'] || this.keys['w']) {
                    this.playerTank.moveUp();
                }
                if (this.keys['ArrowDown'] || this.keys['s']) {
                    this.playerTank.moveDown();
                }
                if (this.keys['ArrowLeft'] || this.keys['a']) {
                    this.playerTank.moveLeft();
                }
                if (this.keys['ArrowRight'] || this.keys['d']) {
                    this.playerTank.moveRight();
                }
                
                // 边界检查
                this.playerTank.constrainToCanvas(GAME_CONFIG.canvasWidth, GAME_CONFIG.canvasHeight);
            }
            
            updateBullets() {
                // 更新玩家子弹
                for (let i = this.bullets.length - 1; i >= 0; i--) {
                    const bullet = this.bullets[i];
                    bullet.update();
                    
                    // 检查是否超出边界
                    if (bullet.isOutOfBounds(GAME_CONFIG.canvasWidth, GAME_CONFIG.canvasHeight)) {
                        this.bullets.splice(i, 1);
                        continue;
                    }
                    
                    // 检查与敌人坦克的碰撞
                    for (let j = this.enemyTanks.length - 1; j >= 0; j--) {
                        const enemy = this.enemyTanks[j];
                        if (this.checkCollision(bullet, enemy)) {
                            enemy.takeDamage();
                            this.bullets.splice(i, 1);
                            
                            if (enemy.isDestroyed()) {
                                this.enemyTanks.splice(j, 1);
                                this.score += 100;
                                this.enemiesDestroyed++;
                            }
                            break;
                        }
                    }
                }
            }
            
            updateEnemyTanks(deltaTime) {
                for (let i = this.enemyTanks.length - 1; i >= 0; i--) {
                    const enemy = this.enemyTanks[i];
                    
                    // 简单的AI移动
                    enemy.simpleAI(GAME_CONFIG.canvasWidth, GAME_CONFIG.canvasHeight, this.headquarters);
                    enemy.update();
                    
                    // 边界检查
                    enemy.constrainToCanvas(GAME_CONFIG.canvasWidth, GAME_CONFIG.canvasHeight);
                    
                    // 检查与玩家坦克的碰撞
                    if (this.checkCollision(enemy, this.playerTank)) {
                        this.playerTank.takeDamage();
                        this.enemyTanks.splice(i, 1);
                        continue;
                    }
                    
                    // 检查与总部基地的碰撞
                    if (this.checkCollision(enemy, this.headquarters)) {
                        this.headquarters.takeDamage();
                        this.enemyTanks.splice(i, 1);
                        continue;
                    }
                }
            }
            
            updateEnemyBullets(deltaTime) {
                // 更新敌人开火计时器
                this.enemyFireTimer += deltaTime;
                
                // 敌人坦克开火
                for (const enemy of this.enemyTanks) {
                    if (this.enemyFireTimer >= GAME_CONFIG.enemyFireRate) {
                        this.enemyFireTimer = 0;
                        this.enemyBullets.push(new Bullet(
                            enemy.x, 
                            enemy.y, 
                            enemy.direction, 
                            'enemy'
                        ));
                    }
                }
                
                // 更新子弹位置
                for (let i = this.enemyBullets.length - 1; i >= 0; i--) {
                    const bullet = this.enemyBullets[i];
                    bullet.update();
                    
                    // 检查是否超出边界
                    if (bullet.isOutOfBounds(GAME_CONFIG.canvasWidth, GAME_CONFIG.canvasHeight)) {
                        this.enemyBullets.splice(i, 1);
                        continue;
                    }
                    
                    // 检查与玩家坦克的碰撞
                    if (this.checkCollision(bullet, this.playerTank)) {
                        this.playerTank.takeDamage();
                        this.enemyBullets.splice(i, 1);
                        continue;
                    }
                    
                    // 检查与总部基地的碰撞
                    if (this.checkCollision(bullet, this.headquarters)) {
                        this.headquarters.takeDamage();
                        this.enemyBullets.splice(i, 1);
                    }
                }
            }
            
            spawnEnemies(deltaTime) {
                // 更新敌人生成计时器
                this.enemySpawnTimer += deltaTime;
                
                // 生成新敌人
                if (this.enemySpawnTimer >= GAME_CONFIG.enemySpawnRate && this.enemyTanks.length < 5) {
                    this.enemySpawnTimer = 0;
                    const x = Math.random() * (GAME_CONFIG.canvasWidth - 50) + 25;
                    this.enemyTanks.push(new Tank(x, 50, 'enemy'));
                }
            }
            
            checkCollision(obj1, obj2) {
                return (
                    obj1.x < obj2.x + obj2.width &&
                    obj1.x + obj1.width > obj2.x &&
                    obj1.y < obj2.y + obj2.height &&
                    obj1.y + obj1.height > obj2.y
                );
            }
            
            playerFire() {
                // 限制玩家开火频率
                if (this.playerTank.canFire()) {
                    this.bullets.push(new Bullet(
                        this.playerTank.x + this.playerTank.width / 2 - 2,
                        this.playerTank.y,
                        'up',
                        'player'
                    ));
                    this.playerTank.resetFireCooldown();
                }
            }
            
            checkGameOver() {
                // 检查玩家生命值
                if (this.playerTank.lives <= 0) {
                    this.endGame('游戏结束！你被击败了！');
                    return;
                }
                
                // 检查总部基地
                if (this.headquarters.health <= 0) {
                    this.endGame('游戏结束！你的总部被摧毁了！');
                    return;
                }
            }
            
            checkLevelProgress() {
                // 检查是否达到下一关要求
                if (this.enemiesDestroyed >= this.level * GAME_CONFIG.levelProgressRequirement) {
                    this.level++;
                    this.enemiesDestroyed = 0;
                    
                    // 增加难度
                    GAME_CONFIG.enemyTankSpeed += 0.5;
                    GAME_CONFIG.enemyFireRate -= 200;
                    GAME_CONFIG.enemySpawnRate -= 300;
                    
                    // 确保最小值
                    if (GAME_CONFIG.enemyFireRate < 500) GAME_CONFIG.enemyFireRate = 500;
                    if (GAME_CONFIG.enemySpawnRate < 1000) GAME_CONFIG.enemySpawnRate = 1000;
                }
            }
            
            endGame(message) {
                this.state = GameState.GAME_OVER;
                document.getElementById('gameOverText').textContent = message;
                document.getElementById('finalScore').textContent = `最终得分: ${this.score}`;
                document.getElementById('gameOverOverlay').style.display = 'flex';
                document.getElementById('pauseBtn').disabled = true;
                
                // 取消游戏循环
                if (this.gameLoopId) {
                    cancelAnimationFrame(this.gameLoopId);
                }
            }
            
            updateUI() {
                // 更新分数
                document.getElementById('score').textContent = this.score;
                
                // 更新关卡
                document.getElementById('level').textContent = this.level;
                
                // 更新生命值
                const lifePercentage = (this.playerTank.lives / GAME_CONFIG.playerLives) * 100;
                document.getElementById('lifeFill').style.width = `${lifePercentage}%`;
                
                // 更新关卡进度
                const levelProgress = (this.enemiesDestroyed % GAME_CONFIG.levelProgressRequirement) / 
                                    GAME_CONFIG.levelProgressRequirement * 100;
                document.getElementById('levelFill').style.width = `${levelProgress}%`;
            }
            
            render