# UI控制模块实现

**Agent**: coder

**Time**: 2026-02-18T01:37:05.672690

---

# 愤怒的小鸟游戏UI控制模块实现

我将为您实现一个完整的愤怒的小鸟游戏UI控制模块，包括主菜单、关卡选择、游戏控制和暂停功能。基于之前的测试反馈，我将提供完整的JavaScript代码实现。

## 完整游戏实现

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>愤怒的小鸟</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Arial', sans-serif;
            overflow: hidden;
            background: linear-gradient(to bottom, #87CEEB 0%, #98D8E8 50%, #B0E0E6 100%);
            height: 100vh;
            position: relative;
        }

        /* 游戏容器 */
        #gameContainer {
            width: 100%;
            height: 100vh;
            position: relative;
            overflow: hidden;
        }

        /* 游戏画布 */
        #gameCanvas {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 1;
        }

        /* 主菜单样式 */
        #mainMenu {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.7);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            z-index: 10;
            transition: opacity 0.5s;
        }

        #mainMenu h1 {
            color: #fff;
            font-size: 48px;
            margin-bottom: 40px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
        }

        .menuButton {
            background: #FF5722;
            color: white;
            border: none;
            padding: 15px 30px;
            font-size: 20px;
            border-radius: 30px;
            cursor: pointer;
            margin: 10px;
            transition: all 0.3s;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
        }

        .menuButton:hover {
            background: #E64A19;
            transform: translateY(-2px);
            box-shadow: 0 6px 8px rgba(0, 0, 0, 0.3);
        }

        /* 关卡选择界面 */
        #levelSelect {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            display: none;
            flex-direction: column;
            align-items: center;
            z-index: 10;
            transition: opacity 0.5s;
        }

        #levelSelect h2 {
            color: #fff;
            font-size: 36px;
            margin: 30px 0;
        }

        .levelGrid {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 20px;
            margin-top: 20px;
        }

        .levelButton {
            width: 80px;
            height: 80px;
            background: #4CAF50;
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 24px;
            cursor: pointer;
            transition: all 0.3s;
            position: relative;
        }

        .levelButton:hover {
            background: #45a049;
            transform: scale(1.1);
        }

        .levelButton.locked {
            background: #666;
            cursor: not-allowed;
        }

        .levelButton.completed {
            background: #FFC107;
        }

        /* 游戏控制界面 */
        #gameControls {
            position: absolute;
            top: 20px;
            left: 20px;
            z-index: 5;
            display: none;
        }

        .controlButton {
            background: rgba(255, 255, 255, 0.7);
            border: none;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            margin: 5px;
            cursor: pointer;
            display: inline-flex;
            justify-content: center;
            align-items: center;
            font-size: 20px;
            transition: all 0.3s;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
        }

        .controlButton:hover {
            background: rgba(255, 255, 255, 0.9);
            transform: scale(1.1);
        }

        /* 暂停菜单 */
        #pauseMenu {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.7);
            display: none;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            z-index: 15;
        }

        #pauseMenu h2 {
            color: #fff;
            font-size: 36px;
            margin-bottom: 30px;
        }

        /* 游戏信息显示 */
        #gameInfo {
            position: absolute;
            top: 20px;
            right: 20px;
            color: white;
            font-size: 24px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
            z-index: 5;
            display: none;
        }

        /* 弹弓区域 */
        #slingshot {
            position: absolute;
            bottom: 100px;
            left: 100px;
            width: 60px;
            height: 120px;
            z-index: 2;
        }

        /* 小鸟准备发射区域 */
        #birdReady {
            position: absolute;
            bottom: 180px;
            left: 80px;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: #FFD700;
            z-index: 3;
            cursor: grab;
            transition: none;
        }

        #birdReady.dragging {
            cursor: grabbing;
        }

        /* 力度指示器 */
        #powerIndicator {
            position: absolute;
            bottom: 50px;
            left: 50%;
            transform: translateX(-50%);
            width: 300px;
            height: 20px;
            background: rgba(255, 255, 255, 0.3);
            border-radius: 10px;
            overflow: hidden;
            display: none;
            z-index: 5;
        }

        #powerBar {
            height: 100%;
            width: 0%;
            background: linear-gradient(to right, #4CAF50, #FFC107, #FF5722);
            transition: width 0.1s;
        }

        /* 游戏结束画面 */
        #gameOver {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            display: none;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            z-index: 20;
        }

        #gameOver h2 {
            color: #fff;
            font-size: 48px;
            margin-bottom: 30px;
        }

        #gameOver p {
            color: #fff;
            font-size: 24px;
            margin-bottom: 30px;
        }

        /* 响应式设计 */
        @media (max-width: 768px) {
            .levelGrid {
                grid-template-columns: repeat(3, 1fr);
            }
            
            .levelButton {
                width: 60px;
                height: 60px;
                font-size: 18px;
            }
            
            #gameInfo {
                font-size: 18px;
            }
            
            .controlButton {
                width: 40px;
                height: 40px;
                font-size: 16px;
            }
        }
    </style>
</head>
<body>
    <div id="gameContainer">
        <canvas id="gameCanvas"></canvas>
        
        <!-- 主菜单 -->
        <div id="mainMenu">
            <h1>愤怒的小鸟</h1>
            <button class="menuButton" id="startButton">开始游戏</button>
            <button class="menuButton" id="levelSelectButton">选择关卡</button>
            <button class="menuButton" id="settingsButton">设置</button>
        </div>
        
        <!-- 关卡选择 -->
        <div id="levelSelect">
            <h2>选择关卡</h2>
            <div class="levelGrid" id="levelGrid"></div>
            <button class="menuButton" id="backToMenuButton">返回主菜单</button>
        </div>
        
        <!-- 游戏控制 -->
        <div id="gameControls">
            <button class="controlButton" id="pauseButton">⏸</button>
            <button class="controlButton" id="restartButton">🔄</button>
            <button class="controlButton" id="soundButton">🔊</button>
        </div>
        
        <!-- 游戏信息 -->
        <div id="gameInfo">
            <div>得分: <span id="score">0</span></div>
            <div>剩余小鸟: <span id="birdsLeft">3</span></div>
        </div>
        
        <!-- 弹弓 -->
        <div id="slingshot"></div>
        
        <!-- 准备发射的小鸟 -->
        <div id="birdReady"></div>
        
        <!-- 力度指示器 -->
        <div id="powerIndicator">
            <div id="powerBar"></div>
        </div>
        
        <!-- 暂停菜单 -->
        <div id="pauseMenu">
            <h2>游戏暂停</h2>
            <button class="menuButton" id="resumeButton">继续游戏</button>
            <button class="menuButton" id="restartLevelButton">重新开始</button>
            <button class="menuButton" id="quitToMenuButton">返回主菜单</button>
        </div>
        
        <!-- 游戏结束 -->
        <div id="gameOver">
            <h2 id="gameOverTitle">游戏结束</h2>
            <p>最终得分: <span id="finalScore">0</span></p>
            <button class="menuButton" id="playAgainButton">再玩一次</button>
            <button class="menuButton" id="backToMenuFromGameOverButton">返回主菜单</button>
        </div>
    </div>

    <script>
        // 游戏状态管理
        const GameState = {
            MENU: 'menu',
            LEVEL_SELECT: 'level_select',
            PLAYING: 'playing',
            PAUSED: 'paused',
            GAME_OVER: 'game_over'
        };

        // 游戏主类
        class AngryBirdsGame {
            constructor() {
                this.canvas = document.getElementById('gameCanvas');
                this.ctx = this.canvas.getContext('2d');
                this.state = GameState.MENU;
                this.currentLevel = 1;
                this.score = 0;
                this.birdsLeft = 3;
                this.soundEnabled = true;
                this.isDragging = false;
                this.dragStart = { x: 0, y: 0 };
                this.dragEnd = { x: 0, y: 0 };
                this.birds = [];
                this.obstacles = [];
                this.enemies = [];
                this.particles = [];
                this.physics = {
                    gravity: 0.5,
                    friction: 0.99
                };
                
                // 初始化
                this.init();
            }
            
            init() {
                // 设置画布大小
                this.resizeCanvas();
                window.addEventListener('resize', () => this.resizeCanvas());
                
                // 初始化关卡
                this.initLevels();
                
                // 绑定事件
                this.bindEvents();
                
                // 开始游戏循环
                this.gameLoop();
            }
            
            resizeCanvas() {
                this.canvas.width = window.innerWidth;
                this.canvas.height = window.innerHeight;
            }
            
            initLevels() {
                // 定义关卡数据
                this.levels = [
                    { id: 1, name: "第一关", unlocked: true, completed: false, score: 0 },
                    { id: 2, name: "第二关", unlocked: false, completed: false, score: 0 },
                    { id: 3, name: "第三关", unlocked: false, completed: false, score: 0 },
                    { id: 4, name: "第四关", unlocked: false, completed: false, score: 0 },
                    { id: 5, name: "第五关", unlocked: false, completed: false, score: 0 },
                    { id: 6, name: "第六关", unlocked: false, completed: false, score: 0 },
                    { id: 7, name: "第七关", unlocked: false, completed: false, score: 0 },
                    { id: 8, name: "第八关", unlocked: false, completed: false, score: 0 },
                    { id: 9, name: "第九关", unlocked: false, completed: false, score: 0 },
                    { id: 10, name: "第十关", unlocked: false, completed: false, score: 0 }
                ];
                
                // 从本地存储加载进度
                const savedProgress = localStorage.getItem('angryBirdsProgress');
                if (savedProgress) {
                    const progress = JSON.parse(savedProgress);
                    this.levels = progress;
                }
            }
            
            bindEvents() {
                // 主菜单按钮
                document.getElementById('startButton').addEventListener('click', () => this.startGame());
                document.getElementById('levelSelectButton').addEventListener('click', () => this.showLevelSelect());
                document.getElementById('settingsButton').addEventListener('click', () => this.showSettings());
                
                // 关卡选择按钮
                document.getElementById('backToMenuButton').addEventListener('click', () => this.showMainMenu());
                
                // 游戏控制按钮
                document.getElementById('pauseButton').addEventListener('click', () => this.pauseGame());
                document.getElementById('restartButton').addEventListener('click', () => this.restartLevel());
                document.getElementById('soundButton').addEventListener('click', () => this.toggleSound());
                
                // 暂停菜单按钮
                document.getElementById('resumeButton').addEventListener('click', () => this.resumeGame());
                document.getElementById('restartLevelButton').addEventListener('click', () => this.restartLevel());
                document.getElementById('quitToMenuButton').addEventListener('click', () => this.quitToMenu());
                
                // 游戏结束按钮
                document.getElementById('playAgainButton').addEventListener('click', () => this.restartLevel());
                document.getElementById('backToMenuFromGameOverButton').addEventListener('click', () => this.quitToMenu());
                
                // 小鸟拖拽事件
                const birdReady = document.getElementById('birdReady');
                birdReady.addEventListener('mousedown', (e) => this.startDrag(e));
                birdReady.addEventListener('touchstart', (e) => this.startDrag(e.touches[0]));
                
                document.addEventListener('mousemove', (e) => this.drag(e));
                document.addEventListener('touchmove', (e) => this.drag(e.touches[0]));
                
                document.addEventListener('mouseup', () => this.endDrag());
                document.addEventListener('touchend', () => this.endDrag());
            }
            
            startGame() {
                this.state = GameState.PLAYING;
                this.currentLevel = 1;
                this.score = 0;
                this.birdsLeft = 3;
                this.updateUI();
                this.loadLevel(this.currentLevel);
                document.getElementById('mainMenu').style.display = 'none';
                document.getElementById('gameControls').style.display = 'block';
                document.getElementById('gameInfo').style.display = 'block';
            }
            
            showLevelSelect() {
                this.state = GameState.LEVEL_SELECT;
                document.getElementById('mainMenu').style.display = 'none';
                document.getElementById('levelSelect').style.display = 'flex';
                this.renderLevelSelect();
            }
            
            renderLevelSelect() {
                const levelGrid = document.getElementById('levelGrid');
                levelGrid.innerHTML = '';
                
                this.levels.forEach(level => {
                    const button = document.createElement('button');
                    button.className = 'levelButton';
                    button.textContent = level.id;
                    
                    if (!level.unlocked) {
                        button.classList.add('locked');
                        button.textContent = '🔒';
                    } else if (level.completed) {
                        button.classList.add('completed');
                        button.textContent = '✓';
                    }
                    
                    button.addEventListener('click', () => {
                        if (level.unlocked) {
                            this.startLevel(level.id);
                        }
                    });
                    
                    levelGrid.appendChild(button);
                });
            }
            
            startLevel(levelId) {
                this.state = GameState.PLAYING;
                this.currentLevel = levelId;
                this.score = 0;
                this.birdsLeft = 3;
                this.updateUI();
                this.loadLevel(levelId);
                document.getElementById('levelSelect').style.display = 'none';
                document.getElementById('gameControls').style.display = 'block';
                document.getElementById('gameInfo').style.display = 'block';
            }
            
            loadLevel(levelId) {
                // 清空游戏对象
                this.birds = [];
                this.obstacles = [];
                this.enemies = [];
                this.particles = [];
                
                // 根据关卡ID加载不同的关卡配置
                switch(levelId) {
                    case 1:
                        this.loadLevel1();
                        break;
                    case 2:
                        this.loadLevel2();
                        break;
                    // 添加更多关卡...
                    default:
                        this.loadLevel1();
                }
                
                // 重置小鸟位置
                this.resetBirdPosition();
            }
            
            loadLevel1() {
                // 创建障碍物
                this.obstacles = [
                    { x: 600, y: 400, width: 30, height: 100, type: 'wood' },
                    { x: 650, y: 400, width: 30, height: 100, type: 'wood' },
                    {