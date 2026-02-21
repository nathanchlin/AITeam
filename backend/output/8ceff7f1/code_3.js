// 使用requestAnimationFrame进行动画控制
class AnimationManager {
  constructor() {
    this.queuedAnimations = [];
    this.isAnimating = false;
  }
  
  addAnimation(animation) {
    this.queuedAnimations.push(animation);
    if (!this.isAnimating) {
      this.processAnimations();
    }
  }
  
  processAnimations() {
    if (this.queuedAnimations.length === 0) {
      this.isAnimating = false;
      return;
    }
    
    this.isAnimating = true;
    const animation = this.queuedAnimations.shift();
    
    requestAnimationFrame(() => {
      animation();
      this.processAnimations();
    });
  }
}

// 使用防抖处理快速连续操作
function debounce(func, wait) {
  let timeout;
  return function() {
    const context = this;
    const args = arguments;
    clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(context, args), wait);
  };
}