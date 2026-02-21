function showGameMessage(message, type = 'info') {
    const messageEl = document.getElementById('game-message');
    messageEl.textContent = message;
    messageEl.className = `game-message ${type}`;
    messageEl.style.opacity = '1';
    
    setTimeout(() => {
        messageEl.style.opacity = '0';
    }, 2000);
}