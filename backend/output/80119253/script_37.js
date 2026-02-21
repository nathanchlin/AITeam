function renderInstructions() {
    const instructions = document.createElement('div');
    instructions.className = 'instructions';
    
    instructions.innerHTML = `
        <h3>游戏说明</h3>
        <ul>
            <li>黑方先行，双方轮流在棋盘上落子</li>
            <li>先连成五子（横、竖、斜）的一方获胜</li>
            <li>点击"重新开始"按钮可以重置游戏</li>
            <li>使用"悔棋"按钮可以撤销上一步操作</li>
        </ul>
        
        <div class="controls">
            <button id="restart-btn" class="control-btn">重新开始</button>
            <button id="undo-btn" class="control-btn">悔棋</button>
            <button id="pause-btn" class="control-btn">暂停</button>
        </div>
    `;
    
    // 绑定按钮事件
    instructions.querySelector('#restart-btn').addEventListener('click', restartGame);
    instructions.querySelector('#undo-btn').addEventListener('click', undoMove);
    instructions.querySelector('#pause-btn').addEventListener('click', togglePause);
    
    return instructions;
}