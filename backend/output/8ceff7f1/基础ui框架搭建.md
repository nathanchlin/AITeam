# 基础UI框架搭建

**Agent**: coder

**Time**: 2026-02-18T01:06:10.873552

---

# 羊了羊游戏基础UI框架搭建

我将为您创建一个羊了羊游戏的基础UI框架，包含主界面、卡片布局和响应式设计。

## 实现方案

### 1. HTML结构

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>羊了羊 - 消消乐游戏</title>
    <link rel="stylesheet" href="styles.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
</head>
<body>
    <div class="game-container">
        <!-- 游戏头部信息 -->
        <header class="game-header">
            <div class="game-title">
                <h1>羊了羊</h1>
            </div>
            <div class="game-stats">
                <div class="stat-item">
                    <i class="fas fa-clock"></i>
                    <span id="timer">00:00</span>
                </div>
                <div class="stat-item">
                    <i class="fas fa-undo"></i>
                    <span id="moves">0</span>
                </div>
                <div class="stat-item">
                    <i class="fas fa-trophy"></i>
                    <span id="score">0</span>
                </div>
            </div>
        </header>

        <!-- 游戏主体区域 -->
        <main class="game-board">
            <!-- 顶部卡片区 -->
            <div class="card-area top-area">
                <div class="card-stack">
                    <!-- 卡片将通过JavaScript动态生成 -->
                </div>
            </div>
            
            <!-- 中间卡片区 -->
            <div class="card-area middle-area">
                <div class="card-grid">
                    <!-- 卡片将通过JavaScript动态生成 -->
                </div>
            </div>
            
            <!-- 底部卡片区 -->
            <div class="card-area bottom-area">
                <div class="card-stack">
                    <!-- 卡片将通过JavaScript动态生成 -->
                </div>
            </div>
        </main>

        <!-- 游戏控制按钮 -->
        <footer class="game-controls">
            <button id="restart-btn" class="btn btn-primary">
                <i class="fas fa-redo"></i> 重新开始
            </button>
            <button id="help-btn" class="btn btn-secondary">
                <i class="fas fa-question-circle"></i> 游戏帮助
            </button>
        </footer>
    </div>

    <!-- 游戏帮助弹窗 -->
    <div id="help-modal" class="modal">
        <div class="modal-content">
            <span class="close">&times;</span>
            <h2>游戏帮助</h2>
            <p>点击两个相同的卡片即可消除它们。</p>
            <p>消除所有卡片即可获胜！</p>
        </div>
    </div>

    <!-- 游戏结束弹窗 -->
    <div id="game-over-modal" class="modal">
        <div class="modal-content">
            <h2 id="game-over-title">游戏结束</h2>
            <p id="game-over-message">您的得分是: <span id="final-score">0</span></p>
            <button id="play-again-btn" class="btn btn-primary">再玩一次</button>
        </div>
    </div>

    <script src="script.js"></script>
</body>
</html>
```

### 2. CSS样式 (styles.css)

```css
/* 全局样式 */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Arial', sans-serif;
    background-color: #f5f5f5;
    color: #333;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
}

.game-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
    width: 100%;
    flex-grow: 1;
    display: flex;
    flex-direction: column;
}

/* 游戏头部样式 */
.game-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
    padding: 15px;
    background-color: #fff;
    border-radius: 10px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.game-title h1 {
    font-size: 2.5rem;
    color: #ff6b6b;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
}

.game-stats {
    display: flex;
    gap: 20px;
}

.stat-item {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 1.2rem;
    font-weight: bold;
}

.stat-item i {
    color: #4ecdc4;
}

/* 游戏主体样式 */
.game-board {
    flex-grow: 1;
    display: flex;
    flex-direction: column;
    gap: 20px;
    position: relative;
}

.card-area {
    background-color: rgba(255, 255, 255, 0.8);
    border-radius: 10px;
    padding: 20px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.top-area {
    height: 150px;
    display: flex;
    justify-content: center;
    align-items: flex-start;
}

.middle-area {
    flex-grow: 1;
    display: flex;
    justify-content: center;
    align-items: center;
}

.bottom-area {
    height: 200px;
    display: flex;
    justify-content: center;
    align-items: flex-end;
}

.card-stack {
    position: relative;
    width: 100%;
    max-width: 300px;
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
}

.card-grid {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    grid-template-rows: repeat(7, 1fr);
    gap: 10px;
    width: 100%;
    max-width: 500px;
    height: 100%;
    max-height: 500px;
}

/* 卡片样式 */
.card {
    width: 60px;
    height: 80px;
    background-color: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 2rem;
    position: relative;
    overflow: hidden;
}

.card:hover {
    transform: translateY(-5px);
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
}

.card.selected {
    border: 3px solid #4ecdc4;
    transform: scale(1.05);
}

.card.matched {
    opacity: 0;
    transform: scale(0);
    pointer-events: none;
}

.card.disabled {
    pointer-events: none;
    opacity: 0.7;
}

.card-front, .card-back {
    position: absolute;
    width: 100%;
    height: 100%;
    backface-visibility: hidden;
    display: flex;
    justify-content: center;
    align-items: center;
    border-radius: 8px;
}

.card-front {
    background-color: #fff;
    transform: rotateY(180deg);
}

.card-back {
    background-color: #ff6b6b;
    transform: rotateY(0deg);
}

/* 控制按钮样式 */
.game-controls {
    display: flex;
    justify-content: center;
    gap: 20px;
    margin-top: 30px;
}

.btn {
    padding: 12px 24px;
    border: none;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: bold;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    gap: 8px;
}

.btn-primary {
    background-color: #4ecdc4;
    color: white;
}

.btn-primary:hover {
    background-color: #45b7b8;
}

.btn-secondary {
    background-color: #ff6b6b;
    color: white;
}

.btn-secondary:hover {
    background-color: #ff5252;
}

/* 弹窗样式 */
.modal {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
    z-index: 1000;
    justify-content: center;
    align-items: center;
}

.modal-content {
    background-color: white;
    padding: 30px;
    border-radius: 10px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    max-width: 500px;
    width: 90%;
    text-align: center;
    position: relative;
}

.close {
    position: absolute;
    top: 15px;
    right: 20px;
    font-size: 24px;
    cursor: pointer;
    color: #aaa;
}

.close:hover {
    color: #333;
}

/* 响应式设计 */
@media (max-width: 768px) {
    .game-title h1 {
        font-size: 1.8rem;
    }
    
    .game-stats {
        gap: 10px;
    }
    
    .stat-item {
        font-size: 1rem;
    }
    
    .card {
        width: 40px;
        height: 55px;
        font-size: 1.5rem;
    }
    
    .card-grid {
        grid-template-columns: repeat(5, 1fr);
        grid-template-rows: repeat(5, 1fr);
        gap: 8px;
    }
    
    .game-controls {
        flex-direction: column;
        gap: 10px;
    }
    
    .btn {
        width: 100%;
    }
}

@media (max-width: 480px) {
    .game-title h1 {
        font-size: 1.5rem;
    }
    
    .card {
        width: 30px;
        height: 40px;
        font-size: 1.2rem;
    }
    
    .card-grid {
        grid-template-columns: repeat(4, 1fr);
        grid-template-rows: repeat(4, 1fr);
        gap: 5px;
    }
    
    .modal-content {
        padding: 20px;
    }
}
```

### 3. JavaScript基础框架 (script.js)

```javascript
// 游戏配置
const gameConfig = {
    cardTypes: ['🐑', '🐐', '🐴', '🐮', '🐷', '🐵', '🐶', '🐱', '🐭'], // 卡片类型（羊的变体）
    gridRows: 7,
    gridCols: 7,
    maxTopCards: 5,
    maxBottomCards: 5,
    gameTimeLimit: 300, // 5分钟
};

// 游戏状态
let gameState = {
    cards: [],
    selectedCards: [],
    moves: 0,
    score: 0,
    timeLeft: gameConfig.gameTimeLimit,
    timerInterval: null,
    isGameOver: false,
};

// DOM元素
const elements = {
    timer: document.getElementById('timer'),
    moves: document.getElementById('moves'),
    score: document.getElementById('score'),
    topArea: document.querySelector('.top-area .card-stack'),
    middleArea: document.querySelector('.middle-area .card-grid'),
    bottomArea: document.querySelector('.bottom-area .card-stack'),
    restartBtn: document.getElementById('restart-btn'),
    helpBtn: document.getElementById('help-btn'),
    helpModal: document.getElementById('help-modal'),
    gameOverModal: document.getElementById('game-over-modal'),
    playAgainBtn: document.getElementById('play-again-btn'),
    closeModal: document.querySelector('.close'),
    finalScore: document.getElementById('final-score'),
};

// 初始化游戏
function initGame() {
    resetGameState();
    createCards();
    renderCards();
    startTimer();
    attachEventListeners();
}

// 重置游戏状态
function resetGameState() {
    gameState.cards = [];
    gameState.selectedCards = [];
    gameState.moves = 0;
    gameState.score = 0;
    gameState.timeLeft = gameConfig.gameTimeLimit;
    gameState.isGameOver = false;
    
    if (gameState.timerInterval) {
        clearInterval(gameState.timerInterval);
    }
    
    updateUI();
}

// 创建卡片数据
function createCards() {
    // 创建中间区域的卡片
    for (let i = 0; i < gameConfig.gridRows * gameConfig.gridCols; i++) {
        const cardType = gameConfig.cardTypes[Math.floor(Math.random() * gameConfig.cardTypes.length)];
        gameState.cards.push({
            id: i,
            type: cardType,
            area: 'middle',
            position: i,
            isFlipped: false,
            isMatched: false,
        });
    }
    
    // 创建顶部区域的卡片
    let cardId = gameConfig.gridRows * gameConfig.gridCols;
    for (let i = 0; i < gameConfig.maxTopCards; i++) {
        const cardType = gameConfig.cardTypes[Math.floor(Math.random() * gameConfig.cardTypes.length)];
        gameState.cards.push({
            id: cardId++,
            type: cardType,
            area: 'top',
            position: i,
            isFlipped: false,
            isMatched: false,
        });
    }
    
    // 创建底部区域的卡片
    for (let i = 0; i < gameConfig.maxBottomCards; i++) {
        const cardType = gameConfig.cardTypes[Math.floor(Math.random() * gameConfig.cardTypes.length)];
        gameState.cards.push({
            id: cardId++,
            type: cardType,
            area: 'bottom',
            position: i,
            isFlipped: false,
            isMatched: false,
        });
    }
}

// 渲染卡片
function renderCards() {
    // 清空所有区域
    elements.topArea.innerHTML = '';
    elements.middleArea.innerHTML = '';
    elements.bottomArea.innerHTML = '';
    
    // 渲染每个区域的卡片
    const areas = ['top', 'middle', 'bottom'];
    areas.forEach(area => {
        const areaElement = area === 'top' ? elements.topArea : 
                          area === 'middle' ? elements.middleArea : elements.bottomArea;
        
        const areaCards = gameState.cards.filter(card => card.area === area && !card.isMatched);
        
        areaCards.forEach(card => {
            const cardElement = createCardElement(card);
            areaElement.appendChild(cardElement);
        });
    });
}

// 创建卡片元素
function createCardElement(card) {
    const cardDiv = document.createElement('div');
    cardDiv.className = 'card';
    cardDiv.dataset.cardId = card.id;
    
    // 如果卡片在顶部或底部区域，显示背面
    if (card.area === 'top' || card.area === 'bottom') {
        cardDiv.innerHTML = `
            <div class="card-back"></div>
            <div class="card-front">${card.type}</div>
        `;
    } else {
        // 中间区域的卡片直接显示正面
        cardDiv.innerHTML = `
            <div class="card-front">${card.type}</div>
        `;
    }
    
    // 添加点击事件
    cardDiv.addEventListener('click', () => handleCardClick(card.id));
    
    return cardDiv;
}

// 处理卡片点击
function handleCardClick(cardId) {
    if (gameState.isGameOver) return;
    
    const card = gameState.cards.find(c => c.id === cardId);
    if (!card || card.isMatched) return;
    
    // 如果点击的是顶部或底部的卡片，翻转它
    if (card.area === 'top' || card.area === 'bottom') {
        flipCard(card);
    }
    
    // 添加到选中卡片列表
    if (!gameState.selectedCards.includes(cardId)) {
        gameState.selectedCards.push(cardId);
        document.querySelector(`[data-card-id="${cardId}"]`).classList.add('selected');
    }
    
    // 如果选中了两张卡片，检查是否匹配
    if (gameState.selectedCards.length === 2) {
        checkMatch();
    }
}

// 翻转卡片
function flipCard(card) {
    card.isFlipped = !card.isFlipped;
    const cardElement = document.querySelector(`[data-card-id="${card.id}"]`);
    
    if (card.isFlipped) {
        cardElement.classList.add('flipped');
    } else {
        cardElement.classList.remove('flipped');
    }
}

// 检查卡片是否匹配
function checkMatch() {
    const [cardId1, cardId2] = gameState.selectedCards;
    const card1 = gameState.cards.find(c => c.id === cardId1);
    const card2 = gameState.cards.find(c => c.id === cardId2);
    
    gameState.moves++;
    updateUI();
    
    if (card1.type === card2.type) {
        // 匹配成功
        setTimeout(() => {
            card1.isMatched = true;
            card2.isMatched = true;
            
            document.querySelector(`[data-card-id="${cardId1}"]`).classList.add('matched');
            document.querySelector(`[data-card-id="${cardId2}"]`).classList.add('matched');
            
            gameState.score += 100;
            updateUI();
            
            // 检查游戏是否结束
            checkGameOver();
        }, 500);
    } else {
        // 匹配失败
        setTimeout(() => {
            // 如果是顶部或底部的卡片，翻转回去
            if (card1.area === 'top' || card1.area === 'bottom') {
                flipCard(card1);
            }
            if (card2.area === 'top' || card2.area === 'bottom') {
                flipCard(card2);
            }
            
            // 移除选中状态
            document.querySelector(`[data-card-id="${cardId1}"]`).classList.remove('selected');
            document.querySelector(`[data-card-id="${cardId2}"]`).classList.remove('selected');
        }, 1000);
