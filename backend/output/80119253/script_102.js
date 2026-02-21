// 测试用例
function runTests() {
    console.log('开始测试游戏状态管理模块...');
    
    // 测试1: 初始化游戏
    const gameStateManager = new GameStateManager();
    console.log('测试1: 初始化游戏', gameStateManager.getBoard().length === 15 ? '通过' : '失败');
    
    // 测试2: 落子
    const success1 = gameStateManager.placePiece(7, 7);
    console.log('测试2: 落子', success1 ? '通过' : '失败');
    
    // 测试3: 重复落子
    const success2 = gameStateManager.placePiece(7, 7);
    console.log('测试3: 重复落子', !success2 ? '通过' : '失败');
    
    // 测试4: 无效位置落子
    const success3 = gameStateManager.placePiece(-1, 7);
    console.log('测试4: 无效位置落子', !success3 ? '通过' : '失败');
    
    // 测试5: 悔棋
    const success4 = gameStateManager.undo();
    console.log('测试5: 悔棋', success4 ? '通过' : '失败');
    
    // 测试6: 游戏结束后落子
    gameStateManager.placePiece(7, 7);
    gameStateManager.placePiece(7, 8);
    gameStateManager.placePiece(8, 7);
    gameStateManager.placePiece(8, 8);
    gameStateManager.placePiece(9, 7);
    gameStateManager.placePiece(9, 8);
    gameStateManager.placePiece(10, 7);
    gameStateManager.placePiece(10, 8);
    gameStateManager.placePiece(11, 7);
    gameStateManager.placePiece(11, 8);
    gameStateManager.placePiece(12, 7); // 黑子获胜
    const status = gameStateManager.getGameStatus();
    const success5 = gameStateManager.placePiece(12, 8);
    console.log('测试6: 游戏结束后落子', status === GameStatus.WIN && !success5 ? '通过' : '失败');
    
    // 测试7: 胜负判断
    gameStateManager.reset();
    // 构建一个横向五子连珠
    for (let i = 5; i < 10; i++) {
        gameStateManager.placePiece(7, i);
    }
    const winStatus = gameStateManager.getGameStatus();
    const winningLine = gameStateManager.getWinningLine();
    console.log('测试7: 胜负判断', winStatus === GameStatus.WIN && winningLine.length === 5 ? '通过' : '失败');
    
    // 测试8: 平局判断
    gameStateManager.reset();
    // 填满棋盘
    for (let row = 0; row < 15; row++) {
        for (let col = 0; col < 15; col++) {
            gameStateManager.placePiece(row, col);
        }
    }
    const drawStatus = gameStateManager.getGameStatus();
    console.log('测试8: 平局判断', drawStatus === GameStatus.DRAW ? '通过' : '失败');
    
    console.log('测试完成!');
}

// 运行测试
runTests();