function createParticleEffect(x, y) {
     for (let i = 0; i < 12; i++) {
       const particle = document.createElement('div');
       particle.className = 'particle';
       particle.style.left = x + 'px';
       particle.style.top = y + 'px';
       document.body.appendChild(particle);
       
       gsap.to(particle, {
         x: (Math.random() - 0.5) * 200,
         y: (Math.random() - 0.5) * 200,
         opacity: 0,
         duration: 0.8,
         ease: "power2.out",
         onComplete: () => particle.remove()
       });
     }
   }