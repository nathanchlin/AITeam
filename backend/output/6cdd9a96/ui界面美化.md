# UI界面美化

**Agent**: coder

**Time**: 2026-02-17T18:35:48.921156

---

# UI界面美化方案

我将为消消乐游戏设计一个美观、现代的界面，包括背景、宝石样式、按钮和消息提示等元素。以下是完整的HTML文件，包含所有必要的CSS和JavaScript代码。

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>宝石消消乐</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #1a2a6c, #2a4385, #3d5a9c);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            overflow: hidden;
        }

        /* 游戏容器 */
        .game-container {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }

        /* 游戏标题 */
        .game-header {
            text-align: center;
            margin-bottom: 20px;
        }

        .game-title {
            color: #fff;
            font-size: 2.5rem;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
            margin-bottom: 10px;
            letter-spacing: 2px;
            background: linear-gradient(45deg, #f093fb, #f5576c);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        /* 分数显示 */
        .score-container {
            display: flex;
            justify-content: space-between;
            margin-bottom: 20px;
            padding: 10px 20px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
        }

        .score-item {
            color: #fff;
            font-size: 1.2rem;
            display: flex;
            align-items: center;
        }

        .score-label {
            margin-right: 10px;
            opacity: 0.8;
        }

        .score-value {
            font-weight: bold;
            font-size: 1.4rem;
            text-shadow: 0 0 10px rgba(255, 255, 255, 0.5);
        }

        /* 游戏网格 */
        .game-board {
            display: grid;
            grid-template-columns: repeat(8, 1fr);
            grid-gap: 5px;
            background: rgba(0, 0, 0, 0.2);
            padding: 10px;
            border-radius: 10px;
            margin-bottom: 20px;
        }

        /* 宝石基础样式 */
        .gem {
            width: 60px;
            height: 60px;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s ease;
            position: relative;
            display: flex;
            justify-content: center;
            align-items: center;
            font-size: 30px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
        }

        .gem:hover {
            transform: scale(1.1);
            z-index: 10;
        }

        .gem.selected {
            animation: pulse 1s infinite;
            box-shadow: 0 0 20px rgba(255, 255, 255, 0.8);
        }

        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.1); }
            100% { transform: scale(1); }
        }

        /* 宝石颜色样式 */
        .gem-red {
            background: linear-gradient(135deg, #ff6b6b, #ee5a52);
        }

        .gem-blue {
            background: linear-gradient(135deg, #4dabf7, #339af0);
        }

        .gem-green {
            background: linear-gradient(135deg, #51cf66, #40c057);
        }

        .gem-yellow {
            background: linear-gradient(135deg, #ffd43b, #fab005);
        }

        .gem-purple {
            background: linear-gradient(135deg, #cc5de8, #ae3ec9);
        }

        .gem-orange {
            background: linear-gradient(135deg, #ff922b, #fd7e14);
        }

        /* 消除动画 */
        .gem.removing {
            animation: disappear 0.5s forwards;
        }

        @keyframes disappear {
            0% { transform: scale(1); opacity: 1; }
            50% { transform: scale(1.3); opacity: 0.5; }
            100% { transform: scale(0); opacity: 0; }
        }

        /* 下落动画 */
        .gem.falling {
            animation: fall 0.5s ease-in;
        }

        @keyframes fall {
            from { transform: translateY(-400px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }

        /* 控制按钮 */
        .controls {
            display: flex;
            justify-content: center;
            gap: 15px;
        }

        .btn {
            padding: 12px 24px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            border-radius: 30px;
            font-size: 1rem;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
        }

        .btn:active {
            transform: translateY(0);
        }

        /* 消息提示 */
        .message {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 20px 40px;
            border-radius: 15px;
            font-size: 1.5rem;
            font-weight: bold;
            text-align: center;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.3s ease;
            z-index: 100;
        }

        .message.show {
            opacity: 1;
            pointer-events: auto;
        }

        /* 特效背景 */
        .particles {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;
            z-index: -1;
        }

        .particle {
            position: absolute;
            width: 4px;
            height: 4px;
            background: rgba(255, 255, 255, 0.5);
            border-radius: 50%;
            animation: float 10s infinite linear;
        }

        @keyframes float {
            from {
                transform: translateY(100vh) translateX(0);
                opacity: 0;
            }
            10% {
                opacity: 1;
            }
            90% {
                opacity: 1;
            }
            to {
                transform: translateY(-100vh) translateX(100px);
                opacity: 0;
            }
        }

        /* 响应式设计 */
        @media (max-width: 768px) {
            .gem {
                width: 40px;
                height: 40px;
                font-size: 20px;
            }
            
            .game-title {
                font-size: 1.8rem;
            }
            
            .score-item {
                font-size: 1rem;
            }
            
            .score-value {
                font-size: 1.2rem;
            }
        }
    </style>
</head>
<body>
    <!-- 特效背景 -->
    <div class="particles" id="particles"></div>

    <!-- 游戏容器 -->
    <div class="game-container">
        <!-- 游戏标题 -->
        <div class="game-header">
            <h1 class="game-title">宝石消消乐</h1>
        </div>

        <!-- 分数显示 -->
        <div class="score-container">
            <div class="score-item">
                <span class="score-label">分数:</span>
                <span class="score-value" id="score">0</span>
            </div>
            <div class="score-item">
                <span class="score-label">步数:</span>
                <span class="score-value" id="moves">0</span>
            </div>
            <div class="score-item">
                <span class="score-label">目标:</span>
                <span class="score-value" id="target">1000</span>
            </div>
        </div>

        <!-- 游戏网格 -->
        <div class="game-board" id="gameBoard"></div>

        <!-- 控制按钮 -->
        <div class="controls">
            <button class="btn" id="newGameBtn">新游戏</button>
            <button class="btn" id="hintBtn">提示</button>
            <button class="btn" id="shuffleBtn">重排</button>
        </div>
    </div>

    <!-- 消息提示 -->
    <div class="message" id="message"></div>

    <script>
        // 游戏配置
        const BOARD_SIZE = 8;
        const GEM_TYPES = ['💎', '💠', '🔷', '🔶', '🟣', '🟠'];
        const GEM_CLASSES = ['gem-red', 'gem-blue', 'gem-green', 'gem-yellow', 'gem-purple', 'gem-orange'];
        
        // 游戏状态
        let board = [];
        let score = 0;
        let moves = 0;
        let selectedGem = null;
        let isProcessing = false;
        let targetScore = 1000;

        // 初始化游戏
        function initGame() {
            score = 0;
            moves = 0;
            updateScore();
            createBoard();
            fillBoard();
            renderBoard();
            
            // 创建粒子背景
            createParticles();
        }

        // 创建游戏板
        function createBoard() {
            board = Array(BOARD_SIZE).fill(null).map(() => Array(BOARD_SIZE).fill(null));
        }

        // 填充游戏板
        function fillBoard() {
            for (let row = 0; row < BOARD_SIZE; row++) {
                for (let col = 0; col < BOARD_SIZE; col++) {
                    if (board[row][col] === null) {
                        board[row][col] = getRandomGem();
                    }
                }
            }
            
            // 确保初始状态没有匹配
            while (checkMatches().length > 0) {
                removeMatches();
                fillBoard();
            }
        }

        // 获取随机宝石
        function getRandomGem() {
            const randomIndex = Math.floor(Math.random() * GEM_TYPES.length);
            return {
                type: GEM_TYPES[randomIndex],
                class: GEM_CLASSES[randomIndex]
            };
        }

        // 渲染游戏板
        function renderBoard() {
            const gameBoard = document.getElementById('gameBoard');
            gameBoard.innerHTML = '';
            
            for (let row = 0; row < BOARD_SIZE; row++) {
                for (let col = 0; col < BOARD_SIZE; col++) {
                    const gem = document.createElement('div');
                    gem.className = `gem ${board[row][col].class}`;
                    gem.textContent = board[row][col].type;
                    gem.dataset.row = row;
                    gem.dataset.col = col;
                    gem.addEventListener('click', handleGemClick);
                    gameBoard.appendChild(gem);
                }
            }
        }

        // 处理宝石点击
        function handleGemClick(e) {
            if (isProcessing) return;
            
            const row = parseInt(e.target.dataset.row);
            const col = parseInt(e.target.dataset.col);
            
            if (!selectedGem) {
                selectedGem = { row, col };
                e.target.classList.add('selected');
            } else {
                const prevRow = selectedGem.row;
                const prevCol = selectedGem.col;
                
                // 检查是否相邻
                if (isAdjacent(row, col, prevRow, prevCol)) {
                    // 交换宝石
                    swapGems(row, col, prevRow, prevCol);
                    
                    // 检查匹配
                    const matches = checkMatches();
                    if (matches.length > 0) {
                        moves++;
                        updateScore();
                        processMatches(matches);
                    } else {
                        // 没有匹配，交换回来
                        swapGems(row, col, prevRow, prevCol);
                    }
                } else {
                    // 选择新的宝石
                    document.querySelector('.gem.selected')?.classList.remove('selected');
                    selectedGem = { row, col };
                    e.target.classList.add('selected');
                }
            }
        }

        // 检查两个位置是否相邻
        function isAdjacent(row1, col1, row2, col2) {
            const rowDiff = Math.abs(row1 - row2);
            const colDiff = Math.abs(col1 - col2);
            return (rowDiff === 1 && colDiff === 0) || (rowDiff === 0 && colDiff === 1);
        }

        // 交换宝石
        function swapGems(row1, col1, row2, col2) {
            const temp = board[row1][col1];
            board[row1][col1] = board[row2][col2];
            board[row2][col2] = temp;
        }

        // 检查匹配
        function checkMatches() {
            const matches = [];
            
            // 检查水平匹配
            for (let row = 0; row < BOARD_SIZE; row++) {
                for (let col = 0; col < BOARD_SIZE - 2; col++) {
                    const gemType = board[row][col].type;
                    if (gemType && gemType === board[row][col + 1].type && gemType === board[row][col + 2].type) {
                        const match = [{ row, col }, { row, col: col + 1 }, { row, col: col + 2 }];
                        
                        // 检查是否有更多相同的宝石
                        let k = col + 3;
                        while (k < BOARD_SIZE && board[row][k].type === gemType) {
                            match.push({ row, col: k });
                            k++;
                        }
                        
                        matches.push(match);
                        col = k - 1; // 跳过已匹配的宝石
                    }
                }
            }
            
            // 检查垂直匹配
            for (let col = 0; col < BOARD_SIZE; col++) {
                for (let row = 0; row < BOARD_SIZE - 2; row++) {
                    const gemType = board[row][col].type;
                    if (gemType && gemType === board[row + 1][col].type && gemType === board[row + 2][col].type) {
                        const match = [{ row, col }, { row: row + 1, col }, { row: row + 2, col }];
                        
                        // 检查是否有更多相同的宝石
                        let k = row + 3;
                        while (k < BOARD_SIZE && board[k][col].type === gemType) {
                            match.push({ row: k, col });
                            k++;
                        }
                        
                        matches.push(match);
                        row = k - 1; // 跳过已匹配的宝石
                    }
                }
            }
            
            return matches;
        }

        // 处理匹配
        function processMatches(matches) {
            isProcessing = true;
            
            // 标记要移除的宝石
            const gemsToRemove = new Set();
            matches.forEach(match => {
                match.forEach(gem => {
                    gemsToRemove.add(`${gem.row},${gem.col}`);
                });
            });
            
            // 添加移除动画
            gemsToRemove.forEach(key => {
                const [row, col] = key.split(',').map(Number);
                const gemElement = document.querySelector(`[data-row="${row}"][data-col="${col}"]`);
                if (gemElement) {
                    gemElement.classList.add('removing');
                }
            });
            
            // 计算分数
            const points = gemsToRemove.size * 10;
            score += points;
            updateScore();
            
            // 显示分数提示
            if (gemsToRemove.size >= 4) {
                showMessage(`连击! +${points}分`);
            }
            
            // 检查是否达到目标
            if (score >= targetScore) {
                setTimeout(() => {
                    showMessage('恭喜你赢了!');
                    setTimeout(() => {
                        if (confirm('游戏胜利! 是否开始新游戏?')) {
                            initGame();
                        }
                    }, 1500);
                }, 600);
            }
            
            // 移除宝石并填充新宝石
            setTimeout(() => {
                removeMatches(gemsToRemove);
                dropGems();
                fillEmptySpaces();
                
                // 检查是否有新的匹配
                setTimeout(() => {
                    const newMatches = checkMatches();
                    if (newMatches.length > 0) {
                        processMatches(newMatches);
                    } else {
                        isProcessing = false;
                        selectedGem = null;
                        document.querySelector('.gem.selected')?.classList.remove('selected');
                    }
                }, 500);
            }, 500);
        }

        // 移除匹配的宝石
        function removeMatches(gemsToRemove) {
            gemsToRemove.forEach(key => {
                const [row, col] = key.split(',').map(Number);
                board[row][col] = null;
            });
        }

        // 宝石下落
        function dropGems() {
            for (let col = 0; col < BOARD_SIZE; col++) {
                let emptyRow = BOARD_SIZE - 1;
                
                for (let row = BOARD_SIZE - 1