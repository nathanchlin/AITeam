let lastTime = 0;
const targetFPS = 60;
const frameInterval = 1000 / targetFPS;

function gameLoop(currentTime) {
  requestAnimationFrame(gameLoop);
  
  const deltaTime = currentTime - lastTime;
  
  if (deltaTime >= frameInterval) {
    updateGameState();
    render();
    lastTime = currentTime - (deltaTime % frameInterval);
  }
}

requestAnimationFrame(gameLoop);