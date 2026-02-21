let lastTime = 0;
   function gameLoop(timestamp) {
     const deltaTime = timestamp - lastTime;
     lastTime = timestamp;
     
     updateGameState(deltaTime);
     render();
     
     requestAnimationFrame(gameLoop);
   }