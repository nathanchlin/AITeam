function animateScoreChange(oldScore, newScore) {
    const scoreElement = document.getElementById('score');
    const scoreDiff = newScore - oldScore;
    
    if (scoreDiff > 0) {
        // 创建浮动分数效果
        const floatingScore = document.createElement('div');
        floatingScore.className = 'floating-score';
        floatingScore.textContent = `+${scoreDiff}`;
        floatingScore.style.position = 'absolute';
        floatingScore.style.left = '50%';
        floatingScore.style.top = '50%';
        floatingScore.style.transform = 'translate(-50%, -50%)';
        
        scoreElement.parentElement.appendChild(floatingScore);
        
        // 动画效果
        floatingScore.animate([
            { transform: 'translate(-50%, -50%) scale(0.5)', opacity: 1 },
            { transform: 'translate(-50%, -150%) scale(1.2)', opacity: 0 }
        ], {
            duration: 1000,
            easing: 'ease-out'
        }).onfinish = () => floatingScore.remove();
    }
    
    // 更新分数
    scoreElement.textContent = newScore;
    scoreElement.style.transform = 'scale(1.1)';
    
    setTimeout(() => {
        scoreElement.style.transform = 'scale(1)';
    }, 200);
}