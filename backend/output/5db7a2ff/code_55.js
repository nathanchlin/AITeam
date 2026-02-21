// 滑动方向指示器
class SwipeIndicator {
    constructor() {
        this.indicator = document.createElement('div');
        this.indicator.className = 'swipe-indicator';
        document.body.appendChild(this.indicator);
    }
    
    show(x1, y1, x2, y2) {
        const angle = Math.atan2(y2 - y1, x2 - x1) * 180 / Math.PI;
        const distance = Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2));
        
        this.indicator.style.left = `${x1}px`;
        this.indicator.style.top = `${y1}px`;
        this.indicator.style.width = `${distance}px`;
        this.indicator.style.transform = `rotate(${angle}deg)`;
        this.indicator.style.opacity = '1';
        
        setTimeout(() => {
            this.indicator.style.opacity = '0';
        }, 300);
    }
}