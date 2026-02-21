// 使用GSAP或原生Web Animations API实现消除动画
function removeCardWithAnimation(cardElement) {
  // 方案1: 使用GSAP
  gsap.to(cardElement, {
    duration: 0.5,
    scale: 0,
    rotation: 360,
    ease: "power2.inOut",
    onComplete: () => {
      cardElement.remove();
    }
  });
  
  // 方案2: 使用Web Animations API (原生)
  const animation = cardElement.animate([
    { transform: 'scale(1) rotate(0deg)', opacity: 1 },
    { transform: 'scale(0) rotate(360deg)', opacity: 0 }
  ], {
    duration: 500,
    easing: 'cubic-bezier(0.4, 0.0, 0.2, 1)',
    fill: 'forwards'
  });
  
  animation.onfinish = () => cardElement.remove();
}