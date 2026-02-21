let frameCount = 0;
let lastFPSUpdate = 0;
let currentFPS = 0;

function updateFPS(currentTime) {
  frameCount++;
  if (currentTime - lastFPSUpdate >= 1000) {
    currentFPS = frameCount;
    frameCount = 0;
    lastFPSUpdate = currentTime;
    console.log(`FPS: ${currentFPS}`);
  }
}