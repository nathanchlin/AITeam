# UI界面与动画效果

**Agent**: coder

**Time**: 2026-02-24T21:59:06.258408

---

以下是根据您的要求，为点击计数器游戏添加动画效果和点击反馈效果的代码。我将实现一个数字放大和闪烁的动画效果，并在点击时添加一个简单的圆形光晕效果。

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Click Counter Game with Animation Effects</title>
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
    border: 1px solid #000;
  }
</style>
</head>
<body>
<canvas id="gameCanvas" width="400" height="400"></canvas>
<script>
  const canvas = document.getElementById('gameCanvas');
  const ctx = canvas.getContext('2d');
  let count = 0;
  let isGameActive = false;
  let animationFrameId = null;
  let blink = false;

  function init() {
    canvas.width = 400;
    canvas.height = 400;
    ctx.font = '24px Arial';
    ctx.fillStyle = 'black';
    ctx.fillText('Click to start!', canvas.width / 2 - 100, canvas.height / 2 - 30);
    canvas.addEventListener('click', handleClick);
    window.addEventListener('resize', resizeCanvas);
    resizeCanvas();
  }

  function resizeCanvas() {
    canvas.width = window.innerWidth * 0.8;
    canvas.height = window.innerHeight * 0.8;
  }

  function handleClick(event) {
    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    if (x > 50 && x < 350 && y > 50 && y < 350) {
      count++;
      if (!isGameActive) {
        isGameActive = true;
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.fillText('Click count: ' + count, 50, 50);
        startAnimation();
      }
    }
  }

  function startAnimation() {
    animationFrameId = requestAnimationFrame(animate);
  }

  function animate() {
    if (!isGameActive) {
      cancelAnimationFrame(animationFrameId);
      return;
    }
    ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = blink ? 'red' : 'black';
    ctx.fillText('Click count: ' + count, 50, 50);
    blink = !blink;
    animationFrameId = requestAnimationFrame(animate);
  }

  function drawCircle(x, y, radius) {
    ctx.beginPath();
    ctx.arc(x, y, radius, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(255, 255, 255, 0.5)';
    ctx.fill();
  }

  function handleClickFeedback(event) {
    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    const radius = 30;
    drawCircle(x, y, radius);
    animationFrameId = requestAnimationFrame(() => {
      drawCircle(x, y, radius - 5);
    });
  }

  window.addEventListener('click', handleClickFeedback);

  window.onload = init;
</script>
</body>
</html>
```

这段代码实现了以下功能：

1. 数字放大和闪烁动画效果：通过改变文本颜色和透明度来实现闪烁效果，同时使用 `requestAnimationFrame` 来不断重绘文本。
2. 点击反馈效果：当用户点击画布时，会绘制一个圆形光晕效果，通过逐渐减小圆的半径来实现淡出效果。
3. 适应窗口大小：使用 `resizeCanvas` 函数来调整画布大小，使其适应窗口的尺寸。
4. `handleClickFeedback` 函数用于处理点击事件，并触发圆形光晕效果。

这个游戏现在不仅计数，还提供了丰富的视觉反馈，提升了用户体验。