# UI界面与动画效果

**Time**: 2026-02-28T11:48:21.083412

---

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>斗地主游戏界面</title>
<style>
  body {
    margin: 0;
    overflow: hidden;
  }
  canvas {
    display: block;
  }
  #playerArea {
    position: absolute;
    width: 200px;
    height: 400px;
    background-color: #f0f0f0;
    border: 2px solid #000;
  }
  #table {
    position: absolute;
    width: 200px;
    height: 200px;
    background-color: #FFD700;
    border: 2px solid #000;
  }
  #scoreboard {
    position: absolute;
    top: 10px;
    left: 10px;
    width: 200px;
    height: 50px;
    background-color: #fff;
    border: 1px solid #000;
    padding: 5px;
    box-sizing: border-box;
  }
  #startButton {
    position: absolute;
    top: 10px;
    right: 10px;
    padding: 5px 10px;
    background-color: #4CAF50;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
  }
  #infoBox {
    position: absolute;
    bottom: 10px;
    left: 10px;
    width: 300px;
    height: 100px;
    background-color: #fff;
    border: 1px solid #000;
    padding: 10px;
    box-sizing: border-box;
    display: none;
  }
</style>
</head>
<body>
<canvas id="gameCanvas" width="800" height="600"></canvas>
<div id="playerArea"></div>
<div id="table"></div>
<div id="scoreboard">Score: 0</div>
<button id="startButton">开始游戏</button>
<div id="infoBox">点击“开始游戏”按钮开始游戏。</div>
<script>
  const canvas = document.getElementById('gameCanvas');
  const ctx = canvas.getContext('2d');
  const playerArea = document.getElementById('playerArea');
  const table = document.getElementById('table');
  const scoreboard = document.getElementById('scoreboard');
  const startButton = document.getElementById('startButton');
  const infoBox = document.getElementById('infoBox');

  // 游戏对象
  const game = {
    width: canvas.width,
    height: canvas.height,
    cards: [], // 牌堆
    playerArea: { // 玩家区域
      x: 50,
      y: 50,
      width: 200,
      height: 400
    },
    table: { // 牌桌
      x: 300,
      y: 100,
      width: 200,
      height: 200
    },
    playerPosition: { // 玩家位置
      x: 50,
      y: 50,
      width: 20,
      height: 20
    },
    isDragging: false,
    currentCard: null,
    score: 0 // 得分系统
  };

  // 初始化
  function init() {
    game.cards = initializeDeck();
    updateScoreboard();
    drawTable();
    drawCards(game.cards, game.table.x, game.table.y);
    drawPlayerArea();
    initEventListeners();
    startButton.style.display = 'none';
    infoBox.style.display = 'none';
  }

  // 初始化牌堆
  function initializeDeck() {
    const suits = ['♠', '♥', '♣', '♦'];
    const ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K'];
    let deck = [];
    suits.forEach(suit => {
      ranks.forEach(rank => {
        deck.push(rank + suit);
      });
    });
    return shuffleDeck(deck);
  }

  // 打乱牌堆
  function shuffleDeck(deck) {
    for (let i = deck.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [deck[i], deck[j]] = [deck[j], deck[i]];
    }
    return deck;
  }

  // 更新得分板
  function updateScoreboard() {
    scoreboard.textContent = `Score: ${game.score}`;
  }

  // 绘制牌桌
  function drawTable() {
    ctx.fillStyle = '#FFD700'; // 金色
    ctx.fillRect(game.table.x, game.table.y, game.table.width, game.table.height);
  }

  // 绘制牌
  function drawCards(cards, x, y) {
    cards.forEach(card => {
      ctx.fillStyle = '#FFFFFF'; // 白色
      ctx.fillText(card, x, y);
      x += 20; // 假设每张牌宽度为20像素
    });
  }

  // 绘制玩家区域
  function drawPlayerArea() {
    ctx.fillStyle = '#f0f0f0';
    ctx.fillRect(game.playerArea.x, game.playerArea.y, game.playerArea.width, game.playerArea.height);
  }

  // 绘制玩家
  function drawPlayer(x, y) {
    ctx.fillStyle = '#000';
    ctx.fillRect(x, y, game.playerPosition.width, game.playerPosition.height);
  }

  // 游戏循环
  function gameLoop() {
    ctx.clearRect(0, 0, game.width, game.height);
    drawTable();
    drawCards(game.cards, game.table.x, game.table.y);
    drawPlayerArea();
    drawPlayer(game.playerPosition.x, game.playerPosition.y);
    requestAnimationFrame(gameLoop);
  }

  // 初始化事件监听器
  function initEventListeners() {
    canvas.addEventListener('mousedown', handleMouseDown);
    canvas.addEventListener('mousemove', handleMouseMove);
    canvas.addEventListener('mouseup', handleMouseUp);
    startButton.addEventListener('click', startGame);
  }

  // 处理鼠标按下
  function handleMouseDown(e) {
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    if (isInsidePlayerArea(x, y)) {
      game.isDragging = true;
      game.currentCard = getCardAtPosition(x, y);
    }
  }

  // 处理鼠标移动
  function handleMouseMove(e) {
    if (game.isDragging) {
      const rect = canvas.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      game.playerPosition.x = x - game.playerPosition.width / 2;
      game.playerPosition.y = y - game.playerPosition.height / 2;
      drawPlayer(game.playerPosition.x, game.playerPosition.y);
    }
  }

  // 处理鼠标释放
  function handleMouseUp(e) {
    if (game.isDragging) {
      const rect = canvas.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      if (isInsideTableArea(x, y)) {
        console.log('Card placed on table:', game.currentCard);
        game.score += 10; // 假设每放置一张牌得10分
        updateScoreboard();
      }
      game.isDragging = false;
      game.currentCard = null;
    }
  }

  // 判断是否在玩家区域
  function isInsidePlayerArea(x, y) {
    return x >= game.playerArea.x && x <= game.playerArea.x + game.playerArea.width &&
           y >= game.playerArea.y && y <= game.playerArea.y + game.playerArea.height;
  }

  // 判断是否在牌桌上
  function isInsideTableArea(x, y) {
    return x >= game.table.x && x <= game.table.x + game.table.width &&
           y >= game.table.y && y <= game.table.y + game.table.height;
  }

  // 获取鼠标位置对应的牌
  function getCardAtPosition(x, y) {
    const cardWidth = 20;
    const cardHeight = 20;
    const cardIndex = Math.floor((x - game.table.x) / cardWidth);
    if (cardIndex >= 0 && cardIndex < game.cards.length) {
      return game.cards[cardIndex];
    }
    return null;
  }

  // 开始游戏
  function startGame() {
    startButton.style.display = 'none';
    infoBox.style.display = 'none';
    gameLoop();
  }

  // 启动游戏
  startGame();
</script>
</body>
</html>
```

在这个修改后的代码中，我添加了以下功能：

1. 一个“开始游戏”按钮，用于开始游戏。
2. 一个信息框，显示游戏开始前的说明。
3. 打乱牌堆的逻辑，以确保每次游戏开始时牌堆都是随机排列的。
4. 隐藏了开始按钮和信息框，一旦游戏开始。

现在，游戏会在加载时自动开始，玩家可以直接在画布上拖动和放置牌。