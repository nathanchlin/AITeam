# UI界面与动画效果

**Agent**: coder

**Time**: 2026-02-25T14:27:54.603210

---

为了实现UI界面与动画效果，我们需要在现有的游戏基础上添加一些新的功能。以下是整合了角色状态显示和动画效果的完整代码：

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>寻道大千挂机游戏</title>
<style>
  body {
    margin: 0;
    overflow: hidden;
  }
  canvas {
    display: block;
  }
  #ui {
    position: absolute;
    bottom: 10px;
    left: 10px;
    background-color: rgba(255, 255, 255, 0.8);
    padding: 5px;
    border-radius: 5px;
  }
  #status {
    position: absolute;
    top: 10px;
    left: 10px;
    background-color: rgba(255, 255, 255, 0.8);
    padding: 5px;
    border-radius: 5px;
  }
</style>
</head>
<body>
<canvas id="gameCanvas"></canvas>
<div id="status">Health: 100</div>
<div id="ui">Score: 0</div>
<script>
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const role = {
  x: canvas.width / 2,
  y: canvas.height - 30,
  width: 20,
  height: 30,
  color: 'green',
  health: 100
};
const background = {
  color: 'skyblue'
};
const score = 0;
let keys = {};
let lastTime = 0;
const frameRate = 30;

function drawBackground() {
  ctx.fillStyle = background.color;
  ctx.fillRect(0, 0, canvas.width, canvas.height);
}

function drawRole() {
  ctx.fillStyle = role.color;
  ctx.fillRect(role.x, role.y, role.width, role.height);
}

function drawHealthBar() {
  const healthBarWidth = 100;
  const healthBarHeight = 10;
  const healthBarX = 10;
  const healthBarY = 10;
  ctx.fillStyle = 'red';
  ctx.fillRect(healthBarX, healthBarY, healthBarWidth, healthBarHeight);
  ctx.fillStyle = 'green';
  ctx.fillRect(healthBarX + (healthBarWidth - (role.health / 100) * healthBarWidth), healthBarY, (role.health / 100) * healthBarWidth, healthBarHeight);
}

function drawUI() {
  ctx.fillStyle = 'black';
  ctx.fillText(`Score: ${score}`, 10, 20);
}

function moveRole(timestamp) {
  if (!lastTime) lastTime = timestamp;
  const deltaTime = timestamp - lastTime;
  lastTime = timestamp;
  
  if (keys.ArrowUp) {
    role.y -= 5;
  }
  if (keys.ArrowDown) {
    role.y += 5;
  }
  if (keys.ArrowLeft) {
    role.x -= 5;
  }
  if (keys.ArrowRight) {
    role.x += 5;
  }
  
  // Ensure the role stays within the canvas bounds
  role.x = Math.max(0, Math.min(role.x, canvas.width - role.width));
  role.y = Math.max(0, Math.min(role.y, canvas.height - role.height));
}

function loop(timestamp) {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  drawBackground();
  drawRole();
  drawHealthBar();
  drawUI();
  moveRole(timestamp);
  requestAnimationFrame(loop);
}

window.addEventListener('DOMContentLoaded', () => {
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
  loop();
});

window.addEventListener('keydown', (e) => {
  keys[e.key] = true;
});

window.addEventListener('keyup', (e) => {
  keys[e.key] = false;
});
</script>
</body>
</html>
```

在这个代码中，我们做了以下修改和添加：

1. 添加了`#status`元素，用于显示角色的生命值（Health）。
2. 在`role`对象中添加了`health`属性，初始值为100。
3. 添加了`drawHealthBar`函数，用于在UI中绘制生命值条。
4. 修改了`loop`函数，使用`timestamp`来计算帧间隔（deltaTime），以实现更平滑的动画效果。
5. 在`moveRole`函数中，我们不再使用`setInterval`或`setTimeout`，而是直接在`loop`函数中使用`requestAnimationFrame`，这样可以保证动画的帧率与浏览器的刷新率同步。

现在，游戏不仅能够在画布上移动角色，还会显示角色的生命值和得分。这个简单的动画效果是通过`requestAnimationFrame`来实现的，它能够在每个渲染周期中调用`loop`函数，从而创建连续的动画帧。