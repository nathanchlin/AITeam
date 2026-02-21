function startGameAnimation() {
    const gameBoard = document.getElementById('game-board');
    gameBoard.style.opacity = '0';
    gameBoard.style.transform = 'scale(0.8)';
    
    setTimeout(() => {
        gameBoard.style.transition = 'all 0.5s ease-out';
        gameBoard.style.opacity = '1';
        gameBoard.style.transform = 'scale(1)';
    }, 100);
}