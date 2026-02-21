class Game {
public:
    void initialize();
    void run();
    void shutdown();
    
private:
    void processInput();
    void update(float deltaTime);
    void render();
    
    std::unique_ptr<GameStateManager> gameStateManager;
    std::unique_ptr<Renderer> renderer;
    std::unique_ptr<PhysicsEngine> physicsEngine;
    std::unique_ptr<InputController> inputController;
    
    // 游戏对象
    std::unique_ptr<Ball> ball;
    std::unique_ptr<Paddle> paddle;
    std::vector<std::unique_ptr<Brick>> bricks;
};