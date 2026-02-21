class AnimationManager {
  constructor() {
    this.animations = [];
  }
  
  update() {
    // 更新所有动画
    for (let i = this.animations.length - 1; i >= 0; i--) {
      const animation = this.animations[i];
      animation.update();
      
      if (animation.isComplete()) {
        this.animations.splice(i, 1);
      }
    }
  }
  
  addAnimation(animation) {
    this.animations.push(animation);
  }
  
  hasAnimations() {
    return this.animations.length > 0;
  }
}