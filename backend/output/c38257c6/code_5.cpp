class InputSystem {
private:
    // 输入状态
    struct InputState {
        bool leftPressed;
        bool rightPressed;
        bool spacePressed;
        bool escapePressed;
    };
    
    InputState currentState;
    InputState previousState;
    
public:
    void update();
    bool isKeyPressed(SDL_Scancode key) const;
    bool isKeyJustPressed(SDL_Scancode key) const;
    bool isKeyJustReleased(SDL_Scancode key) const;
    
    // 控制挡板移动
    void handlePaddleMovement(Paddle& paddle, float deltaTime);
    
    // 处理游戏控制
    void handleGameControls(GameStateManager& stateManager);
};