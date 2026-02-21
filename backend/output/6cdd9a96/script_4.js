// 根据设备性能调整渲染质量
   function adjustQuality() {
     const isLowEnd = detectLowEndDevice();
     const gems = document.querySelectorAll('.gem');
     
     gems.forEach(gem => {
       if (isLowEnd) {
         gem.style.transition = 'transform 0.2s, opacity 0.2s';
         gem.style.boxShadow = 'none';
       } else {
         gem.style.transition = 'transform 0.3s, opacity 0.3s, box-shadow 0.3s';
         gem.style.boxShadow = '0 2px 4px rgba(0,0,0,0.2)';
       }
     });
   }