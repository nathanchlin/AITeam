class MatchAnimation extends BaseAnimation {
  constructor(matchedGems, onComplete) {
    super(400, 'ease-in-out');
    this.matchedGems = matchedGems;
    this.onComplete = onComplete;
    this.originalScales = matchedGems.map(gem => gem.scale || 1);
    this.originalOpacity = matchedGems.map(gem => gem.opacity || 1);
  }

  apply(progress) {
    // 消除动画：缩小并淡出
    const scaleProgress = Math.sin(progress * Math.PI);
    const opacityProgress = 1 - progress;
    
    this.matchedGems.forEach((gem, i) => {
      gem.scale = this.originalScales[i] * scaleProgress;
      gem.opacity = this.originalOpacity[i] * opacityProgress;
      
      // 添加轻微的旋转效果
      gem.rotation = (1 - progress) * 360 * (i % 2 === 0 ? 1 : -1);
    });
    
    // 添加粒子效果
    if (progress > 0.5 && !this.particlesCreated) {
      this.createParticles();
      this.particlesCreated = true;
    }
  }

  createParticles() {
    this.matchedGems.forEach(gem => {
      for (let i = 0; i < 8; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        particle.style.left = `${gem.x * cellSize + cellSize / 2}px`;
        particle.style.top = `${gem.y * cellSize + cellSize / 2}px`;
        particle.style.backgroundColor = gem.color;
        particle.style.width = '8px';
        particle.style.height = '8px';
        particle.style.borderRadius = '50%';
        particle.style.position = 'absolute';
        particle.style.pointerEvents = 'none';
        gameBoard.appendChild(particle);
        
        // 粒子动画
        const angle = (i / 8) * Math.PI * 2;
        const velocity = 100 + Math.random() * 50;
        const lifetime = 1000 + Math.random() * 500;
        
        let startTime = performance.now();
        
        const animateParticle = () => {
          const elapsed = performance.now() - startTime;
          const progress = Math.min(elapsed / lifetime, 1);
          
          if (progress < 1) {
            const distance = velocity * progress;
            particle.style.transform = `translate(${Math.cos(angle) * distance}px, ${Math.sin(angle) * distance}px)`;
            particle.style.opacity = 1 - progress;
            requestAnimationFrame(animateParticle);
          } else {
            particle.remove();
          }
        };
        
        requestAnimationFrame(animateParticle);
      }
    });
  }

  isComplete() {
    if (super.isComplete()) {
      this.matchedGems.forEach(gem => {
        gem.scale = 1;
        gem.opacity = 1;
        gem.rotation = 0;
      });
      if (this.onComplete) this.onComplete();
      return true;
    }
    return false;
  }
}