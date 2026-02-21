// 全局错误捕获
window.addEventListener('error', (event) => {
    const errorData = {
        timestamp: new Date().toISOString(),
        message: event.message,
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno,
        error: event.error ? event.error.stack : null,
        userAgent: navigator.userAgent,
        gameVersion: "1.0.0"
    };
    
    // 发送错误信息到服务器
    fetch('https://yourapi.com/errors', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(errorData)
    });
});