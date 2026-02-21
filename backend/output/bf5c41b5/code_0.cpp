class GameStateManager {
public:
    enum class GameState {
        MENU,
        PLAYING,
        PAUSED,
        GAME_OVER,
        LEVEL_COMPLETE
    };
    
    void update(float deltaTime);
    void setState(GameState newState);
    GameState getCurrentState() const;
    void resetGame();
    
private:
    GameState currentState;
    int currentLevel;
    int score;
    int lives;
    std::vector<std::unique_ptr<GameObject>> gameObjects;
};