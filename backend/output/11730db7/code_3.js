class InputHandler {
  constructor(canvas) {
    this.canvas = canvas;
    this.selectedTile = null;
    this.isDragging = false;
    
    // 绑定事件监听器
    this.canvas.addEventListener('mousedown', this.handleMouseDown.bind(this));
    this.canvas.addEventListener('mousemove', this.handleMouseMove.bind(this));
    this.canvas.addEventListener('mouseup', this.handleMouseUp.bind(this));
    this.canvas.addEventListener('touchstart', this.handleTouchStart.bind(this));
    this.canvas.addEventListener('touchmove', this.handleTouchMove.bind(this));
    this.canvas.addEventListener('touchend', this.handleTouchEnd.bind(this));
  }
  
  handleMouseDown(event) {
    const rect = this.canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    
    this.handleTileSelection(x, y);
  }
  
  handleMouseMove(event) {
    if (!this.isDragging) return;
    
    const rect = this.canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    
    this.handleTileSelection(x, y);
  }
  
  handleMouseUp(event) {
    this.isDragging = false;
    this.selectedTile = null;
  }
  
  handleTouchStart(event) {
    event.preventDefault();
    const rect = this.canvas.getBoundingClientRect();
    const touch = event.touches[0];
    const x = touch.clientX - rect.left;
    const y = touch.clientY - rect.top;
    
    this.handleTileSelection(x, y);
  }
  
  handleTouchMove(event) {
    event.preventDefault();
    if (!this.isDragging) return;
    
    const rect = this.canvas.getBoundingClientRect();
    const touch = event.touches[0];
    const x = touch.clientX - rect.left;
    const y = touch.clientY - rect.top;
    
    this.handleTileSelection(x, y);
  }
  
  handleTouchEnd(event) {
    event.preventDefault();
    this.isDragging = false;
    this.selectedTile = null;
  }
  
  handleTileSelection(x, y) {
    const tileSize = 50;
    const padding = 5;
    const startX = (this.canvas.width - (8 * (tileSize + padding))) / 2;
    const startY = (this.canvas.height - (8 * (tileSize + padding))) / 2;
    
    const col = Math.floor((x - startX) / (tileSize + padding));
    const row = Math.floor((y - startY) / (tileSize + padding));
    
    if (row >= 0 && row < 8 && col >= 0 && col < 8) {
      if (!this.selectedTile) {
        // 第一次选择
        this.selectedTile = { row, col };
      } else {
        // 第二次选择，尝试交换
        if (this.isAdjacent(this.selectedTile, { row, col })) {
          // 触发交换事件
          this.emitSwapEvent(this.selectedTile, { row, col });
        }
        this.selectedTile = null;
      }
    }
  }
  
  isAdjacent(tile1, tile2) {
    const rowDiff = Math.abs(tile1.row - tile2.row);
    const colDiff = Math.abs(tile1.col - tile2.col);
    
    return (rowDiff === 1 && colDiff === 0) || (rowDiff === 0 && colDiff === 1);
  }
  
  emitSwapEvent(tile1, tile2) {
    // 触发交换事件，由游戏逻辑处理
    const event = new CustomEvent('swapTiles', {
      detail: { tile1, tile2 }
    });
    this.canvas.dispatchEvent(event);
  }
}