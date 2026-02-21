// 粒子效果系统
class ParticleSystem {
  constructor(game) {
    this.game = game;
    this.particles = [];
  }
  
  createExplosion(x, y, color = '#ff9900') {
    // 创建爆炸粒子
    for (let i = 0; i < 30; i++) {
      this.particles.push({
        x: x,
        y: y,
        vx: (Math.random() - 0.5) * 10,
        vy: (Math.random() - 0.5) * 10,
        size: Math.random() * 5 + 2,
        color: color,
        life: 30
      });
    }
  }
  
  createEngineTrail(x, y) {
    // 创建引擎尾迹
    this.particles.push({
      x: x,
      y: y,
      vx: (Math.random() - 0.5) * 2,
      vy: Math.random() * 2 + 1,
      size: Math.random() * 3 + 1,
      color: '#00ccff',
      life: 15
    });
  }
  
  update() {
    // 更新所有粒子
    for (let i = this.particles.length - 1; i >= 0; i--) {
      const p = this.particles[i];
      
      // 更新位置
      p.x += p.vx;
      p.y += p.vy;
      
      // 减少生命值
      p.life--;
      
      // 移除死亡粒子
      if (p.life <= 0) {
        this.particles.splice(i, 1);
      }
    }
  }
  
  render(ctx) {
    // 渲染所有粒子
    this.particles.forEach(p => {
      ctx.globalAlpha = p.life / 30;
      ctx.fillStyle = p.color;
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
      ctx.fill();
    });
    ctx.globalAlpha = 1;
  }
}