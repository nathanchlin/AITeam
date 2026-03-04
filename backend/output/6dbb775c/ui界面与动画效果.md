# UI界面与动画效果

**Agent**: coder

**Time**: 2026-02-24T10:55:07.743024

---

根据您的要求，以下是整合了碰撞检测和得分系统的黑白棋游戏代码。这段代码是一个完整的单文件HTML，包含内联CSS和JavaScript，可以直接运行。

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>黑白棋游戏</title>
<style>
  body {
    margin: 0;
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    background-color: #f0f0f0;
  }
  canvas {
    border: 2px solid #000;
  }
  #scoreboard {
    position: absolute;
    top: 10px;
    left: 10px;
  }
</style>
</head>
<body>
<canvas id="gameCanvas" width="400" height="400"></canvas>
<div id="scoreboard">
  <p>Score - Black: <span id="scoreBlack">0</span></p>
  <p>Score - White: <span id="scoreWhite">0</span></p>
</div>
<script>
  const canvas = document.getElementById('gameCanvas');
  const ctx = canvas.getContext('2d');
  const boardSize = 8;
  const cellSize = canvas.width / boardSize;
  let board = [];
  let currentPlayer = 'black';
  let scoreBlack = 0;
  let scoreWhite = 0;

  function initializeBoard() {
    for (let i = 0; i < boardSize; i++) {
      board[i] = [];
      for (let j = 0; j < boardSize; j++) {
        board[i][j] = null;
      }
    }
  }

  function drawBoard() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = 'black';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    for (let i = 0; i < boardSize; i++) {
      for (let j = 0; j < boardSize; j++) {
        ctx.beginPath();
        ctx.moveTo(j * cellSize, i * cellSize);
        ctx.lineTo((j + 1) * cellSize, i * cellSize);
        ctx.lineTo((j + 1) * cellSize, (i + 1) * cellSize);
        ctx.lineTo(j * cellSize, (i + 1) * cellSize);
        ctx.lineTo(j * cellSize, i * cellSize);
        ctx.stroke();
        if (board[i][j]) {
          drawPiece(i, j, board[i][j]);
        }
      }
    }
    drawScore();
  }

  function drawPiece(x, y, color) {
    const offset = 10;
    const pieceSize = cellSize - 2 * offset;
    const startX = x * cellSize + offset;
    const startY = y * cellSize + offset;
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.arc(startX + pieceSize / 2, startY + pieceSize / 2, pieceSize / 2 - 2, 0, 2 * Math.PI);
    ctx.fill();
  }

  function drawScore() {
    document.getElementById('scoreBlack').textContent = scoreBlack;
    document.getElementById('scoreWhite').textContent = scoreWhite;
  }

  function onCanvasClick(event) {
    const x = Math.floor((event.offsetX - 10) / cellSize);
    const y = Math.floor((event.offsetY - 10) / cellSize);
    if (board[x][y] === null) {
      board[x][y] = currentPlayer;
      currentPlayer = currentPlayer === 'black' ? 'white' : 'black';
      updateScore(x, y);
      drawBoard();
    }
  }

  function updateScore(x, y) {
    let surroundedCount = 0;
    // Horizontal
    for (let i = -1; i <= 1; i++) {
      if (x + i >= 0 && x + i < boardSize && y >= 0 && y < boardSize) {
        if (board[x + i][y] !== currentPlayer) {
          surroundedCount++;
        }
      }
    }
    // Vertical
    for (let j = -1; j <= 1; j++) {
      if (x >= 0 && x < boardSize && y + j >= 0 && y + j < boardSize) {
        if (board[x][y + j] !== currentPlayer) {
          surroundedCount++;
        }
      }
    }
    // Diagonal
    for (let i = -1; i <= 1; i++) {
      for (let j = -1; j <= 1; j++) {
        if (x + i >= 0 && x + i < boardSize && y + j >= 0 && y + j < boardSize) {
          if (board[x + i][y + j] !== currentPlayer) {
            surroundedCount++;
          }
        }
      }
    }
    if (surroundedCount >= 3) {
      if (currentPlayer === 'black') {
        scoreBlack++;
      } else {
        scoreWhite++;
      }
    }
  }

  function startGameLoop() {
    requestAnimationFrame(startGameLoop);
    drawBoard();
  }

  window.onload = function() {
    canvas.addEventListener('click', onCanvasClick);
    initializeBoard();
    drawBoard();
    startGameLoop();
  };
</script>
</body>
</html>
```

这段代码实现了一个基本的黑白棋游戏，其中包含了得分系统。当玩家放置棋子时，如果其周围的棋子数达到3个或以上（不包括自己），则获得分数。代码中的得分会实时显示在界面上。