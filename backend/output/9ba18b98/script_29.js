// 双缓冲实现示例
const offscreenCanvas = document.createElement('canvas');
const offscreenCtx = offscreenCanvas.getContext('2d');

function render() {
  // 在离屏Canvas上绘制
  offscreenCtx.clearRect(0, 0, width, height);
  drawGame(offscreenCtx);
  
  // 将离屏Canvas内容复制到主Canvas
  mainCtx.clearRect(0, 0, width, height);
  mainCtx.drawImage(offscreenCanvas, 0, 0);
}