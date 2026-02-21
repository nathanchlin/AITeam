function gameOverAnimation() {
    const gameBoard = document.getElementById('game-board');
    gameBoard.style.transition = 'all 0.5s ease-in';
    gameBoard.style.opacity = '0.7';
    gameBoard.style.filter = 'blur(5px)';
    
    const overlay = document.createElement('div');
    overlay.className = 'game-over-overlay';
    document.body.appendChild(overlay);
    
    setTimeout(() => {
        overlay.style.opacity = '1';
    }, 100);
}