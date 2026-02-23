# UI界面与动画效果

**Agent**: coder

**Time**: 2026-02-22T22:48:55.223672

---

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Jump Game</title>
<style>
  body { margin: 0; overflow: hidden; }
  canvas { display: block; }
  #gameOverText { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: white; font-size: 48px; }
</style>
</head>
<body>
<canvas id="gameCanvas"></canvas>
<div id="gameOverText" style="display: none;"></div>
<script>
  const canvas = document.getElementById('gameCanvas');
  const gameOverText = document.getElementById('gameOverText');
  const ctx = canvas.getContext('2d');

  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;

  const player = {
    x: 50,
    y: canvas.height - 100,
    width: 50,
    height: 50,
    gravity: 0.5,
    jumpHeight: -15,
    velocityY: 0,
    score: 0
  };

  const ground = {
    x: 0,
    y: canvas.height - 50,
    width: canvas.width,
    height: 50
  };

  const obstacles = [];

  function drawPlayer() {
    ctx.fillStyle = 'blue';
    ctx.fillRect(player.x, player.y, player.width, player.height);
  }

  function drawGround() {
    ctx.fillStyle = 'green';
    ctx.fillRect(ground.x, ground.y, ground.width, ground.height);
  }

  function drawObstacles() {
    obstacles.forEach(obstacle => {
      ctx.fillStyle = 'red';
      ctx.fillRect(obstacle.x, obstacle.y, obstacle.width, obstacle.height);
    });
  }

  function drawScore() {
    ctx.fillStyle = 'black';
    ctx.fillText(`Score: ${player.score}`, 10, 30);
  }

  function update() {
    player.velocityY += player.gravity;
    player.y += player.velocityY;

    if (player.y + player.height >= ground.y) {
      player.y = ground.y - player.height;
      player.velocityY = 0;
      gameOver();
    }

    if (player.velocityY < 0) {
      ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
      ctx.fillRect(player.x, player.y + player.height, player.width, 20);
    }

    if (obstacles.length > 0 && player.x < obstacles[0].x && player.x + player.width > obstacles[0].x - obstacles[0].width && player.y < obstacles[0].y) {
      gameOver();
    }

    obstacles.forEach(obstacle => {
      obstacle.x -= 2;
      if (obstacle.x + obstacle.width <= 0) {
        player.score += 10; // Increase score when an obstacle is cleared
      }
    });

    obstacles = obstacles.filter(obstacle => obstacle.x > 0);
  }

  function render() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    drawGround();
    drawPlayer();
    drawObstacles();
    drawScore();
  }

  function gameOver() {
    ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    gameOverText.style.display = 'block';
    cancelAnimationFrame(gameLoop);
  }

  function gameLoop() {
    update();
    render();
    requestAnimationFrame(gameLoop);
  }

  window.onload = function() {
    gameLoop();
  };

  document.addEventListener('keydown', function(event) {
    if (event.code === 'Space' && player.y + player.height === ground.y - player.height) {
      player.velocityY = player.jumpHeight;
    }
  });
</script>
</body>
</html>
```

这段代码实现了一个简单的跳跃游戏，其中包含了得分系统、碰撞检测和游戏结束提示。游戏通过Canvas API渲染，使用`requestAnimationFrame`来创建游戏循环。玩家按下空格键时，玩家角色会跳跃。障碍物会不断地从右侧生成并向左移动，当玩家角色与障碍物碰撞时，游戏结束。得分会在屏幕左上角显示。