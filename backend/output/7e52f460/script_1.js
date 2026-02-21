// 添加触摸事件处理
var touchStartX = 0;
var touchStartY = 0;

canvas.addEventListener('touchstart', function(e) {
    e.preventDefault();
    touchStartX = e.touches[0].clientX;
    touchStartY = e.touches[0].clientY;
}, false);

canvas.addEventListener('touchmove', function(e) {
    e.preventDefault();
}, false);

canvas.addEventListener('touchend', function(e) {
    e.preventDefault();
    var touchEndX = e.changedTouches[0].clientX;
    var touchEndY = e.changedTouches[0].clientY;
    
    var dx = touchEndX - touchStartX;
    var dy = touchEndY - touchStartY;
    
    if (Math.abs(dx) > Math.abs(dy)) {
        // 水平滑动
        if (dx > 0 && direction !== 'left') {
            direction = 'right';
        } else if (dx < 0 && direction !== 'right') {
            direction = 'left';
        }
    } else {
        // 垂直滑动
        if (dy > 0 && direction !== 'up') {
            direction = 'down';
        } else if (dy < 0 && direction !== 'down') {
            direction = 'up';
        }
    }
}, false);