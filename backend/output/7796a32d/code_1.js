class Game {
  constructor() {
    this.config = {
      type: Phaser.AUTO,
      width: 400,
      height: 600,
      physics: {
        default: 'arcade',
        arcade: {
          gravity: { y: 1000 },
          debug: false
        }
      },
      scene: [BootScene, MainMenuScene, GameScene, GameOverScene]
    };
    
    this.game = new Phaser.Game(this.config);
  }
}