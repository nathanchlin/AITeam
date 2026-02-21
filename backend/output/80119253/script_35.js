let gameTimer;

function startTimer() {
    gameTimer = setInterval(() => {
        gameState.timeElapsed++;
        updateTimerDisplay();
    }, 1000);
}

function stopTimer() {
    clearInterval(gameTimer);
}

function updateTimerDisplay() {
    const minutes = Math.floor(gameState.timeElapsed / 60);
    const seconds = gameState.timeElapsed % 60;
    document.getElementById('timer').textContent = 
        `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
}