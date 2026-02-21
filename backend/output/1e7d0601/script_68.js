// 只渲染屏幕可见区域
function renderWithViewport() {
  const viewport = {
    x: Math.max(0, player.x - canvas.width / 2),
    y: Math.max(0, player.y - canvas.height / 2),
    width: canvas.width,
    height: canvas.height
  };
  
  ctx.save();
  ctx.beginPath();
  ctx.rect(viewport.x, viewport.y, viewport.width, viewport.height);
  ctx.clip();
  
  // 只渲染视口内的对象
  renderVisibleObjects(viewport);
  
  ctx.restore();
}