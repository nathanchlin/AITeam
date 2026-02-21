function setupEventListeners() {
    document.addEventListener('keydown', handleKeyPress);
}

function removeEventListeners() {
    document.removeEventListener('keydown', handleKeyPress);
}

function startGame() {
    setupEventListeners();
    // 其他启动代码...
}

function pauseGame() {
    removeEventListeners();
    // 其他暂停代码...
}