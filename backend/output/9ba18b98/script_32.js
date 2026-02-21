let adaptiveQuality = 1.0;

function adjustQuality() {
  const fps = calculateCurrentFPS();
  if (fps < 50) {
    adaptiveQuality = Math.max(0.5, adaptiveQuality - 0.1);
  } else if (fps > 55) {
    adaptiveQuality = Math.min(1.0, adaptiveQuality + 0.1);
  }
  
  // 根据adaptiveQuality调整渲染细节
}