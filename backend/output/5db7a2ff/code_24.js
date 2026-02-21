document.addEventListener('DOMContentLoaded', () => {
    // 初始化游戏控制器
    const gameController = new GameController();
    
    // 绑定新游戏按钮
    document.getElementById('new-game-button').addEventListener('click', () => {
        gameController.restart();
    });
    
    document.querySelector('.retry-button').addEventListener('click', () => {
        gameController.restart();
    });
    
    // 键盘控制
    document.addEventListener('keydown', (event) => {
        switch (event.key) {
            case 'ArrowUp':
                event.preventDefault();
                gameController.move('up');
                break;
            case 'ArrowDown':
                event.preventDefault();
                gameController.move('down');
                break;
            case 'ArrowLeft':
                event.preventDefault();
                gameController.move('left');
                break;
            case 'ArrowRight':
                event.preventDefault();
                gameController.move('right');
                break;
        }
    });
    
    // 触摸控制
    let touchStartX = 0;
    let touchStartY = 0;
    
    document.addEventListener('touchstart', (event) => {
        if (event.touches.length > 0) {
            touchStartX = event.touches[0].clientX;
            touchStartY = event.touches[0].clientY;
        }
    });
    
    document.addEventListener('touchend', (event) => {
        if (!touchStartX || !touchStartY) {
            return;
        }
        
        let touchEndX = 0;
        let touchEndY = 0;
        
        if (event.changedTouches.length > 0) {
            touchEndX = event.changedTouches[0].clientX;
            touchEndY = event.changedTouches[0].clientY;
        }
        
        const dx = touchEndX - touchStartX;
        const dy = touchEndY - touchStartY;
        
        // 确定滑动方向
        if (Math.abs(dx) > Math.abs(dy)) {
            // 水平滑动
            if (dx > 0) {
                gameController.move('right');
            } else {
                gameController.move('left');
            }
        } else {
            // 垂直滑动
            if (dy > 0) {
                gameController.move('down');
            } else {
                gameController.move('up');
            }
        }
        
        touchStartX = 0;
        touchStartY = 0;
    });
});