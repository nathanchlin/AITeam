function gameLoop() {
     updateGameState();
     render();
     requestAnimationFrame(gameLoop);
   }