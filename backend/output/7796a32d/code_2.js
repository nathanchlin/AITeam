class GameState {
  constructor() {
    this.score = 0;
    this.level = 1;
    this.lives = 3;
    this.isGameOver = false;
  }
  
  addScore(points) {
    this.score += points;
  }
  
  nextLevel() {
    this.level++;
  }
  
  loseLife() {
    this.lives--;
    if (this.lives <= 0) {
      this.isGameOver = true;
    }
  }
}