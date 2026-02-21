// 反馈收集函数
function collectFeedback(rating, issue, suggestion, contact) {
    const feedback = {
        timestamp: new Date().toISOString(),
        rating: rating,
        issue: issue,
        suggestion: suggestion,
        contact: contact,
        userAgent: navigator.userAgent,
        screenResolution: `${screen.width}x${screen.height}`,
        gameVersion: "1.0.0" // 从游戏配置中获取
    };
    
    // 发送到服务器
    fetch('https://yourapi.com/feedback', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(feedback)
    })
    .then(response => response.json())
    .then(data => console.log('Feedback submitted:', data))
    .catch(error => console.error('Error submitting feedback:', error));
}