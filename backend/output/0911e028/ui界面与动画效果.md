# UI界面与动画效果

**Agent**: coder

**Time**: 2026-02-21T12:56:21.340410

---

以下是根据您的要求完成的斗地主游戏UI界面和动画效果的设计。代码中包含了动画效果，用于增强用户体验。

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
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    background-color: #f0f0f0;
  }
  canvas {
    border: 2px solid #000;
  }
</style>
</head>
<body>
<canvas id="gameCanvas"></canvas>
<script>
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const scale = 1;
canvas.width = window.innerWidth * scale;
canvas.height = window.innerHeight * scale;

const cardTable = {
  width: 600,
  height: 300,
  x: (canvas.width - 600) / 2,
  y: 50
};

const cardPile = {
  width: 100,
  height: 150,
  x: (canvas.width - 100) / 2,
  y: cardTable.y + cardTable.height + 50
};

const playerArea = {
  width: 300,
  height: 100,
  x: (canvas.width - 300) / 2,
  y: cardTable.y + cardTable.height + 200
};

const cards = ['3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A', '2'];
let playerHand = [];

function shuffleArray(array) {
  for (let i = array.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [array[i], array[j]] = [array[j], array[i]];
  }
}

shuffleArray(cards);
playerHand = cards.slice(0, 17);

function drawCard(x, y, card) {
  ctx.fillStyle = 'red';
  ctx.fillRect(x, y, 70, 100);
  ctx.fillStyle = 'black';
  ctx.fillText(card, x + 35, y + 50);
}

function drawTable() {
  ctx.fillStyle = 'gray';
  ctx.fillRect(cardTable.x, cardTable.y, cardTable.width, cardTable.height);
}

function drawPile() {
  ctx.fillStyle = 'red';
  ctx.fillRect(cardPile.x, cardPile.y, cardPile.width, cardPile.height);
}

function drawPlayerHand() {
  ctx.fillStyle = 'blue';
  ctx.fillRect(playerArea.x, playerArea.y, playerArea.width, playerArea.height);
  playerHand.forEach((card, index) => {
    const cardX = playerArea.x + (cardWidth + 10) * (index % 5);
    const cardY = playerArea.y + (cardHeight + 10) * Math.floor(index / 5);
    drawCard(cardX, cardY, card);
  });
}

function render() {
  ctx.scale(scale, scale);
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  drawTable();
  drawPile();
  drawPlayerHand();

  requestAnimationFrame(render);
}

function init() {
  window.addEventListener('resize', () => {
    canvas.width = window.innerWidth * scale;
    canvas.height = window.innerHeight * scale;
    render();
  });

  canvas.addEventListener('click', (e) => {
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    const clickX = (e.clientX - rect.left) * scaleX;
    const clickY = (e.clientY - rect.top) * scaleY;

    if (clickX > cardPile.x && clickX < cardPile.x + cardPile.width &&
        clickY > cardPile.y && clickY < cardPile.y + cardPile.height) {
      // Animate card to player hand
      animateCardToPlayerHand();
    }
  });

  render();
}

function animateCardToPlayerHand() {
  const cardWidth = 70;
  const cardHeight = 100;
  let targetX = playerArea.x + (cardWidth + 10) * (playerHand.length % 5);
  let targetY = playerArea.y + (cardHeight + 10) * Math.floor(playerHand.length / 5);
  let currentX = cardPile.x;
  let currentY = cardPile.y;
  let step = 10;

  function animate() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    drawTable();
    drawPile();
    drawPlayerHand();

    ctx.beginPath();
    ctx.moveTo(currentX, currentY);
    ctx.lineTo(targetX, targetY);
    ctx.lineWidth = 5;
    ctx.strokeStyle = 'green';
    ctx.stroke();

    currentX += (targetX - currentX) / 10;
    currentY += (targetY - currentY) / 10;

    if (Math.abs(targetX - currentX) > step || Math.abs(targetY - currentY) > step) {
      requestAnimationFrame(animate);
    } else {
      // Add the card to the player's hand
      playerHand.push('3'); // Example card
      render();
    }
  }

  requestAnimationFrame(animate);
}

window.onload = init;
</script>
</body>
</html>
```

这段代码创建了一个斗地主游戏的UI界面，并且添加了一个简单的动画效果，当用户点击牌堆时，会模拟一张牌移动到玩家手中的动画。代码中使用了`requestAnimationFrame`来实现平滑的动画效果，并且通过计算当前位置和目标位置之间的差值来逐步移动卡片。