// 在game.js中添加
window.addEventListener('load', function() {
    const loadingScreen = document.getElementById('loading');
    const gameContainer = document.getElementById('game-container');
    
    // 模拟加载时间
    setTimeout(() => {
        loadingScreen.style.display = 'none';
        gameContainer.style.display = 'block';
        initGame();
    }, 1000);
});