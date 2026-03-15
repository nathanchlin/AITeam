import { Game } from './Game';
import { Renderer } from './Renderer';
import { CONFIG } from './config';
import './styles.css';

class App {
 private game: Game;
 private renderer: Renderer;
 private lastUpdateTime: number =0;
 private speed: number;

 constructor() {
 const canvas = document.getElementById('gameCanvas') as HTMLCanvasElement;
 if (!canvas) {
 throw new Error('Canvas element not found');
 }

 this.game = new Game();
 this.renderer = new Renderer(canvas);
 this.speed = CONFIG.INITIAL_SPEED;

 this.setupInputs();
 this.startLoop();
 }

 private setupInputs(): void {
 window.addEventListener('keydown', (e) => {
 if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', ' '].includes(e.key)) {
 e.preventDefault();
 }

 switch (e.key) {
 case 'ArrowUp':
 case 'w':
 case 'W':
 this.game.setDirection('UP');
 break;
 case 'ArrowDown':
 case 's':
 case 'S':
 this.game.setDirection('DOWN');
 break;
 case 'ArrowLeft':
 case 'a':
 case 'A':
 this.game.setDirection('LEFT');
 break;
 case 'ArrowRight':
 case 'd':
 case 'D':
 this.game.setDirection('RIGHT');
 break;
 case ' ':
 if (this.game.state.isGameOver) {
 this.game.reset();
 this.speed = CONFIG.INITIAL_SPEED;
 } else {
 this.game.togglePause();
 }
 break;
 }
 });
 }

 private startLoop(): void {
 const loop = (timestamp: number) => {
 if (timestamp - this.lastUpdateTime >= this.speed) {
 if (!this.game.state.isPaused && !this.game.state.isGameOver) {
 this.speed = Math.max(50, CONFIG.INITIAL_SPEED - Math.floor(this.game.state.score /50));
 }
 this.game.update();
 this.lastUpdateTime = timestamp;
 }

 this.renderer.draw(this.game.state);
 requestAnimationFrame(loop);
 };

 requestAnimationFrame(loop);
 }
}

window.addEventListener('DOMContentLoaded', () => {
 new App();
});