# 搭建基础HTML框架和Canvas设置

**Agent**: coder

**Time**: 2026-02-17T20:31:24.136921

---

我将为你搭建坦克大战游戏的基础HTML框架和Canvas设置。这是实现游戏的第一步，包含了必要的HTML结构、像素风格CSS样式和Canvas初始化。

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>坦克大战</title>
    <style>
        /* 像素风格重置 */
        * {
            image-rendering: pixelated;
            image-rendering: -moz-crisp-edges;
            image-rendering: crisp-edges;
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Courier New', monospace;
            background-color: #2c2c2c;
            color: #ffffff;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            overflow: hidden;
        }
        
        /* 游戏容器 */
        #game-container {
            position: relative;
            border: 4px solid #444;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.5);
        }
        
        /* Canvas样式 */
        #gameCanvas {
            display: block;
            background-color: #1a1a1a;
            image-rendering: pixelated;
        }
        
        /* 得分显示 */
        #score {
            position: absolute;
            top: 10px;
            left: 10px;
            font-size: 18px;
            font-weight: bold;
            text-shadow: 2px 2px 0 #000;
            z-index: 10;
        }
        
        /* 游戏信息 */
        #game-info {
            margin-top: 20px;
            text-align: center;
            font-size: 14px;
            color: #aaa;
        }
        
        /* 按键提示 */
        .controls {
            margin-top: 10px;
            font-size: 12px;
            color: #888;
        }
    </style>
</head>
<body>
    <div id="game-container">
        <div id="score">得分: 0</div>
        <canvas id="gameCanvas" width="800" height="600"></canvas>
    </div>
    
    <div id="game-info">
        <h2>坦克大战</h2>
        <div class="controls">
            <p>移动: WASD 或 方向键 | 射击: 空格键</p>
        </div>
    </div>

    <script>
        // 获取Canvas元素和上下文
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        
        // 设置Canvas的像素渲染
        ctx.imageSmoothingEnabled = false;
        
        // 游戏常量
        const TILE_SIZE = 20; // 每个瓦片的大小（像素）
        const GRID_WIDTH = canvas.width / TILE_SIZE; // 网格宽度
        const GRID_HEIGHT = canvas.height / TILE_SIZE; // 网格高度
        
        // 游戏状态
        const game = {
            score: 0,
            keys: {},
            player: null,
            enemies: [],
            bullets: [],
            walls: []
        };
        
        // 初始化游戏
        function initGame() {
            console.log('游戏初始化中...');
            
            // 设置Canvas上下文
            ctx.imageSmoothingEnabled = false;
            
            // 这里将在后续步骤中添加游戏对象的初始化
            // 例如：createPlayer(), createEnemies(), createWalls()等
        }
        
        // 游戏循环
        function gameLoop() {
            // 清除画布
            ctx.fillStyle = '#1a1a1a';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            // 更新游戏状态
            update();
            
            // 渲染游戏
            render();
            
            // 继续循环
            requestAnimationFrame(gameLoop);
        }
        
        // 更新游戏状态
        function update() {
            // 这里将在后续步骤中添加游戏逻辑
            // 例如：移动玩家、敌人，检测碰撞等
        }
        
        // 渲染游戏
        function render() {
            // 这里将在后续步骤中添加渲染逻辑
            // 例如：绘制玩家、敌人、子弹、墙壁等
        }
        
        // 键盘事件处理
        document.addEventListener('keydown', (e) => {
            game.keys[e.key.toLowerCase()] = true;
            
            // 防止方向键滚动页面
            if(['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', ' '].includes(e.key)) {
                e.preventDefault();
            }
        });
        
        document.addEventListener('keyup', (e) => {
            game.keys[e.key.toLowerCase()] = false;
        });
        
        // 启动游戏
        window.onload = () => {
            initGame();
            gameLoop();
        };
    </script>
</body>
</html>
```

这个基础框架包含了以下关键部分：

1. **HTML结构**：
   - 包含一个Canvas元素作为游戏主画布
   - 添加了得分显示区域
   - 添加了游戏信息和控制说明

2. **像素风格CSS**：
   - 使用`image-rendering: pixelated`和`image-rendering: crisp-edges`确保像素风格的渲染
   - 设置了深色主题背景，符合复古游戏风格
   - 为游戏容器添加了边框和阴影效果

3. **Canvas设置**：
   - 初始化Canvas上下文，禁用图像平滑处理以保持像素风格
   - 设置了常量定义网格大小和画布尺寸
   - 创建了基本游戏状态对象

4. **游戏循环**：
   - 实现了基本的游戏循环结构（update和render函数）
   - 添加了键盘事件监听器，为后续控制坦克做准备

这个框架为后续实现坦克大战游戏的核心功能（玩家控制、敌人AI、碰撞检测、射击系统等）打下了坚实的基础。下一步将在这个框架基础上添加游戏对象的创建和渲染逻辑。