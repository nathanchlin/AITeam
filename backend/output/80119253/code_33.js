const gameState = {
    isPlaying: false,
    currentPlayer: 'black',
    winner: null,
    moveHistory: [],
    timeElapsed: 0
};

function updateGameState(newState) {
    Object.assign(gameState, newState);
    updateUI();
}