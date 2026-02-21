function initGame() {
     const game = new Game();
     const soundManager = new SoundManager();
     const particleSystem = new ParticleSystem(game);
     const screenShake = new ScreenShake(game);
     const uiFeedback = new UIFeedback(game);
     const difficultyManager = new DifficultyManager(game);
     
     // 将所有组件整合到游戏实例中
     game.addComponent(soundManager);
     game.addComponent(particleSystem);
     game.addComponent(screenShake);
     game.addComponent(uiFeedback);
     game.addComponent(difficultyManager);
     
     return game;
   }