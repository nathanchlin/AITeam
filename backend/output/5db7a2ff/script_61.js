document.addEventListener('keydown', function(e) {
    const key = e.key;
    const validKeys = ['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'];
    
    if (validKeys.includes(key)) {
        e.preventDefault();
        
        // 添加按键视觉反馈
        const keyElement = document.querySelector(`.key-indicator[data-key="${key}"]`);
        if (keyElement) {
            keyElement.classList.add('active');
            setTimeout(() => keyElement.classList.remove('active'), 100);
        }
        
        // 执行游戏逻辑
        handleMove(key);
    }
});