enum GameState {
    MENU,
    PLAYING,
    PAUSED,
    GAME_OVER
};

class GameStateManager {
private:
    GameState currentState;
    std::unordered_map<GameState, std::unique_ptr<State>> states;
    
public:
    void setState(GameState state);
    GameState getCurrentState() const;
    void update(float deltaTime);
    void render();
};