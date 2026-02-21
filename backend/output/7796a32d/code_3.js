class SceneManager {
  constructor(game) {
    this.game = game;
    this.currentScene = null;
  }
  
  switchTo(sceneName) {
    if (this.currentScene) {
      this.currentScene.scene.stop();
    }
    this.currentScene = this.game.scene.getScene(sceneName);
    this.currentScene.scene.start();
  }
}