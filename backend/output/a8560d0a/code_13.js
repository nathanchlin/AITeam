// 检测浏览器支持
if (!window.requestAnimationFrame) {
    window.requestAnimationFrame = window.webkitRequestAnimationFrame || 
                                 window.mozRequestAnimationFrame || 
                                 window.msRequestAnimationFrame || 
                                 function(callback) { return setTimeout(callback, 1000/60); };
}