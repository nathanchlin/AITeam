// 动态UI反馈系统
class UIFeedback {
  constructor(game) {
    this.game = game;
    this.hitEffects = [];
    this.comboEffects = [];
  }
  
  addHitEffect(x, y, damage) {
    this.hitEffects.push({
      x: x,
      y: y,
      text: `-${damage}`,
      life: 30,
      color: damage > 10 ? '#ff3333' : '#ffffff'
    });
  }
  
  addComboEffect(combo) {
    this.comboEffects.push({
      text: `${combo} COMBO!`,
      life: 60,
      scale: 1
    });
  }
  
  update() {
    // 更新命中效果
    for (let i = this.hitEffects.length - 1; i >= 0; i--) {
      const effect = this.hitEffects[i];
      effect.y -= 1;
      effect.life--;
      
      if (effect.life <= 0) {
        this.hitEffects.splice(i, 1);
      }
    }
    
    // 更新连击效果
    for (let i = this.comboEffects.length - 1; i >= 0; i--) {
      const effect = this.comboEffects[i];
      effect.scale += 0.02;
      effect.life--;
      
      if (effect.life <= 0) {
        this.comboEffects.splice(i, 1);
      }
    }
  }
  
  render(ctx) {
    // 渲染命中效果
    this.hitEffects.forEach(effect => {
      ctx.font = '16px Arial';
      ctx.fillStyle = effect.color;
      ctx.globalAlpha = effect.life / 30;
      ctx.fillText(effect.text, effect.x, effect.y);
    });
    
    // 渲染连击效果
    this.comboEffects.forEach(effect => {
      ctx.font = `${24 * effect.scale}px Arial`;
      ctx.fillStyle = '#ffff00';
      ctx.globalAlpha = effect.life / 60;
      ctx.textAlign = 'center';
      ctx.fillText(effect.text, this.game.width / 2, 100);
      ctx.textAlign = 'left';
    });
    
    ctx.globalAlpha = 1;
  }
}