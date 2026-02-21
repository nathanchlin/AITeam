function handleKeyPress(e) {
    if (!gameRunning) return;
    
    switch(e.key) {
        case 'ArrowUp':
            snake.changeDirection({x: 0, y: -1});
            break;
        case 'ArrowDown':
            snake.changeDirection({x: 0, y: 1});
            break;
        case 'ArrowLeft':
            snake.changeDirection({x: -1, y: 0});
            break;
        case 'ArrowRight':
            snake.changeDirection({x: 1, y: 0});
            break;
    }
}