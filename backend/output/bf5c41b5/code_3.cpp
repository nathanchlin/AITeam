class InputController {
public:
    void initialize();
    void update();
    bool isKeyPressed(SDL_Scancode key) const;
    bool isKeyReleased(SDL_Scancode key) const;
    bool isKeyHeld(SDL_Scancode key) const;
    
    // 获取输入状态
    float getHorizontalAxis() const;  // 用于挡板左右移动
    bool isPausePressed() const;
    
private:
    std::unordered_map<SDL_Scancode, bool> keyStates;
};