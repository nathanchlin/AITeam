function addTouchFeedback(element) {
    element.addEventListener('touchstart', function() {
        this.style.opacity = '0.8';
    });
    
    element.addEventListener('touchend', function() {
        this.style.opacity = '1';
    });
}