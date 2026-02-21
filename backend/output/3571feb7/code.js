class Renderer {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    this.ctx = this.canvas.getContext('2d');
    this.width = this.canvas.width;
    this.height = this.canvas.height;
    this.camera = { x: 0, y: 0, zoom: 1 };
    this.backgroundColor = '#000000';
  }

  // 清除画布
  clear() {
    this.ctx.fillStyle = this.backgroundColor;
    this.ctx.fillRect(0, 0, this.width, this.height);
  }

  // 渲染游戏实体
  render(entity) {
    if (!entity.visible) return;
    
    this.ctx.save();
    
    // 应用相机变换
    this.ctx.translate(
      -this.camera.x + this.width / 2, 
      -this.camera.y + this.height / 2
    );
    this.ctx.scale(this.camera.zoom, this.camera.zoom);
    
    // 应用实体变换
    this.ctx.translate(entity.x, entity.y);
    this.ctx.rotate(entity.rotation || 0);
    
    // 渲染实体
    if (entity.render) {
      entity.render(this.ctx);
    }
    
    this.ctx.restore();
  }

  // 渲染文本
  renderText(text, x, y, options = {}) {
    this.ctx.save();
    this.ctx.font = `${options.size || 16}px Arial`;
    this.ctx.fillStyle = options.color || '#FFFFFF';
    this.ctx.textAlign = options.align || 'left';
    this.ctx.fillText(text, x, y);
    this.ctx.restore();
  }

  // 设置相机位置
  setCamera(x, y, zoom) {
    this.camera.x = x;
    this.camera.y = y;
    this.camera.zoom = zoom;
  }
}