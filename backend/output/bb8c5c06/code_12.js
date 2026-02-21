class Renderer {
  constructor(canvas, gridSize) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.gridSize = gridSize;
    this.cellSize = Math.min(
      canvas.width / gridSize,
      canvas.height / gridSize
    );
    
    // 设置画布尺寸
    this.canvas.width = this.cellSize * gridSize;
    this.canvas.height = this.cellSize * gridSize;
  }
}