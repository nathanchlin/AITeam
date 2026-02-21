document.addEventListener('keydown', (e) => {
    if (!gameRunning || gamePaused) return;
    
    switch(e.key) {
        case 'ArrowUp':
            snake.setDirection({x: 0, y: -1});
            break;
        case 'ArrowDown':
            snake.setDirection({x: 0, y: 1});
            break;
        case 'ArrowLeft':
            snake.setDirection({x: -1, y: 0});
            break;
        case 'ArrowRight':
            snake.setDirection({x: 1, y: 0});
            break;
    }
});