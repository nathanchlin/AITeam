// 使用requestAnimationFrame优化动画
   function animateGem(gem, targetX, targetY) {
     const startX = gem.offsetLeft;
     const startY = gem.offsetTop;
     const duration = 300; // 动画持续时间(ms)
     const startTime = performance.now();
     
     function update(currentTime) {
       const elapsed = currentTime - startTime;
       const progress = Math.min(elapsed / duration, 1);
       
       // 使用缓动函数使动画更平滑
       const easeProgress = 1 - Math.pow(1 - progress, 3);
       
       gem.style.transform = `translate(${startX + (targetX - startX) * easeProgress}px, 
                                        ${startY + (targetY - startY) * easeProgress}px)`;
       
       if (progress < 1) {
         requestAnimationFrame(update);
       }
     }
     
     requestAnimationFrame(update);
   }