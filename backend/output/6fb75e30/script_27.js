function jumpAnimation() {
  const stickFigure = document.getElementById('stick-figure');
  stickFigure.style.transition = 'transform 0.2s ease-out';
  
  // 跳跃动画序列
  setTimeout(() => {
    stickFigure.style.transform = 'scaleY(0.8)'; // 压缩
  }, 10);
  
  setTimeout(() => {
    stickFigure.style.transform = 'scaleY(1.2) translateY(-50px)'; // 伸展上升
  }, 100);
  
  setTimeout(() => {
    stickFigure.style.transform = 'scaleY(0.9) translateY(0)'; // 落地压缩
  }, 200);
  
  setTimeout(() => {
    stickFigure.style.transform = 'scaleY(1)'; // 恢复正常
  }, 300);
}