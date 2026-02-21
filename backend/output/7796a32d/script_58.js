// 在game.js中添加
window.addEventListener('error', function(e) {
    console.error('游戏错误:', e.error);
    // 显示用户友好的错误信息
    document.getElementById('error-message').textContent = '游戏加载出现问题，请刷新页面重试。';
});