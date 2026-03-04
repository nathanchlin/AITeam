class ParticleSystem {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.particles = [];
    this.maxParticles = 1000;
  }

  addParticle(x, y, velocity) {
    if (this.particles.length < this.maxParticles) {
      const particle = { x, y, velocity, age: 0 };
      this.particles.push(particle);
    }
  }

  update() {
    for (let i = this.particles.length - 1; i >= 0; i--) {
      const particle = this.particles[i];
      particle.x += particle.velocity.x;
      particle.y += particle.velocity.y;
      particle.age++;

      if (particle.age > 10) {
        this.particles.splice(i, 1);
      }
    }
  }

  render() {
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    this.particles.forEach(particle => {
      this.ctx.fillStyle = 'white';
      this.ctx.beginPath();
      this.ctx.arc(particle.x, particle.y, 2, 0, Math.PI * 2);
      this.ctx.fill();
    });
  }
}