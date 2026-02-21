int main() {
    // 初始化游戏
    Game game;
    PhysicsEngine physics;
    
    // 游戏主循环
    while (game.isRunning()) {
        float deltaTime = getDeltaTime();
        
        // 处理输入
        game.handleInput();
        
        // 更新物理
        physics.update(deltaTime, game);
        
        // 渲染
        game.render();
    }
    
    return 0;
}