class AnimationManager {
  constructor() {
    this.animations = [];
    this.isAnimating = false;
  }

  addAnimation(animation) {
    this.animations.push(animation);
    if (!this.isAnimating) {
      this.isAnimating = true;
      this.animate();
    }
  }

  animate() {
    if (this.animations.length === 0) {
      this.isAnimating = false;
      return;
    }

    const animation = this.animations[0];
    animation.update();
    
    if (animation.isComplete()) {
      this.animations.shift();
      requestAnimationFrame(() => this.animate());
    } else {
      requestAnimationFrame(() => this.animate());
    }
  }

  isAnimating() {
    return this.isAnimating || this.animations.length > 0;
  }
}

// 全局动画管理器
const animationManager = new AnimationManager();