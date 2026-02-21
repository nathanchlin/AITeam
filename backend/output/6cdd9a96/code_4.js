class FallAnimation extends BaseAnimation {
  constructor(gems, onComplete) {
    super(500, 'ease-in-out');
    this.gems = gems;
    this.onComplete = onComplete;
    this.targetPositions = {};
    
    // 计算目标位置
    this.gems.forEach(gem => {
      this.targetPositions[gem.id] = gem.y;
      gem.y = gem.startY;
    });
  }

  apply(progress) {
    // 使用弹性缓动效果
    const bounceProgress = this.easeOutBounce(progress);
    
    this.gems.forEach(gem => {
      const startY = gem.startY;
      const targetY = this.targetPositions[gem.id];
      gem.y = startY + (targetY - startY) * bounceProgress;
      
      // 添加轻微的旋转
      gem.rotation = (1 - progress) * 90 * (gem.id % 2 === 0 ? 1 : -1);
      
      // 缩放效果
      gem.scale = 0.8 + progress * 0.2;
    });
  }

  easeOutBounce(x) {
    const n1 = 7.5625;
    const d1 = 2.75;

    if (x < 1 / d1) {
      return n1 * x * x;
    } else if (x < 2 / d1) {
      return n1 * (x -= 1.5 / d1) * x + 0.75;
    } else if (x < 2.5 / d1) {
      return n1 * (x -= 2.25 / d1) * x + 0.9375;
    } else {
      return n1 * (x -= 2.625 / d1) * x + 0.984375;
    }
  }

  isComplete() {
    if (super.isComplete()) {
      this.gems.forEach(gem => {
        gem.rotation = 0;
        gem.scale = 1;
      });
      if (this.onComplete) this.onComplete();
      return true;
    }
    return false;
  }
}