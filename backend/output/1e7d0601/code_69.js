// 使用精灵图集减少绘制调用
class SpriteAtlas {
  constructor(image, tileWidth, tileHeight) {
    this.image = image;
    this.tileWidth = tileWidth;
    this.tileHeight = tileHeight;
  }
  
  drawTile(ctx, tileIndex, x, y) {
    const cols = this.image.width / this.tileWidth;
    const row = Math.floor(tileIndex / cols);
    const col = tileIndex % cols;
    
    ctx.drawImage(
      this.image,
      col * this.tileWidth, row * this.tileHeight,
      this.tileWidth, this.tileHeight,
      x, y,
      this.tileWidth, this.tileHeight
    );
  }
}