// 渲染器类
class Renderer {
  constructor(canvas, gameMap) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.gameMap = gameMap;
    this.setupCanvas();
  }

  // 设置Canvas尺寸
  setupCanvas() {
    this.canvas.width = this.gameMap.width * this.gameMap.cellSize;
    this.canvas.height = this.gameMap.height * this.gameMap.cellSize;
  }

  // 清除画布
  clear() {
    this.ctx.fillStyle = '#000';
    this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
  }

  // 绘制单元格
  drawCell(x, y, cellType) {
    const pixelX = x * this.gameMap.cellSize;
    const pixelY = y * this.gameMap.cellSize;
    const size = this.gameMap.cellSize;

    switch (cellType) {
      case CELL_TYPES.WALL:
        this.ctx.fillStyle = '#00f';
        this.ctx.fillRect(pixelX, pixelY, size, size);
        break;
        
      case CELL_TYPES.EMPTY:
        this.ctx.fillStyle = '#000';
        this.ctx.fillRect(pixelX, pixelY, size, size);
        break;
        
      case CELL_TYPES.DOT:
        this.ctx.fillStyle = '#000';
        this.ctx.fillRect(pixelX, pixelY, size, size);
        this.ctx.fillStyle = '#ff0';
        this.ctx.beginPath();
        this.ctx.arc(pixelX + size/2, pixelY + size/2, size/6, 0, Math.PI * 2);
        this.ctx.fill();
        break;
        
      case CELL_TYPES.POWER_DOT:
        this.ctx.fillStyle = '#000';
        this.ctx.fillRect(pixelX, pixelY, size, size);
        this.ctx.fillStyle = '#ff0';
        this.ctx.beginPath();
        this.ctx.arc(pixelX + size/2, pixelY + size/2, size/3, 0, Math.PI * 2);
        this.ctx.fill();
        break;
        
      case CELL_TYPES.PACMAN:
        this.ctx.fillStyle = '#000';
        this.ctx.fillRect(pixelX, pixelY, size, size);
        this.ctx.fillStyle = '#ff0';
        this.ctx.beginPath();
        this.ctx.arc(pixelX + size/2, pixelY + size/2, size/2.5, 0.2 * Math.PI, 1.8 * Math.PI);
        this.lineTo(pixelX + size/2, pixelY + size/2);
        this.fill();
        break;
        
      case CELL_TYPES.GHOST:
        this.ctx.fillStyle = '#000';
        this.ctx.fillRect(pixelX, pixelY, size, size);
        this.ctx.fillStyle = '#f00';
        // 绘制鬼魂形状
        this.ctx.beginPath();
        this.ctx.arc(pixelX + size/2, pixelY + size/3, size/2.5, Math.PI, 0);
        this.lineTo(pixelX + size * 0.8, pixelY + size * 0.7);
        this.lineTo(pixelX + size * 0.7, pixelY + size * 0.8);
        this.lineTo(pixelX + size * 0.5, pixelY + size * 0.7);
        this.lineTo(pixelX + size * 0.3, pixelY + size * 0.8);
        this.lineTo(pixelX + size * 0.2, pixelY + size * 0.7);
        this.lineTo(pixelX + size/2, pixelY + size * 0.7);
        this.closePath();
        this.fill();
        break;
    }
  }

  // 渲染整个地图
  render() {
    this.clear();
    
    for (let y = 0; y < this.gameMap.height; y++) {
      for (let x = 0; x < this.gameMap.width; x++) {
        this.drawCell(x, y, this.gameMap.getCell(x, y));
      }
    }
  }
}