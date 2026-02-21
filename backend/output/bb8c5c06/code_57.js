render() {
    // 清除旧食物
    document.querySelectorAll('.food').forEach(cell => {
        cell.classList.remove('food');
    });
    
    // 渲染新食物
    gameBoard[this.position.y][this.position.x].classList.add('food');
}