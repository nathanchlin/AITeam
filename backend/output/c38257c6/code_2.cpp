enum class GameState {
    MENU,        // 菜单状态
    PLAYING,     // 游戏中
    PAUSED,      // 暂停
    GAME_OVER,   // 游戏结束
    WIN          // 胜利
};

class GameStateManager {
private:
    GameState currentState;
    int score;
    int lives;
    int level;
    
    // 游戏对象引用
    std::shared_ptr<Paddle> paddle;
    std::shared_ptr<Ball> ball;
    std::vector<std::shared_ptr<Brick>> bricks;
    
public:
    void update(float deltaTime);
    void setState(GameState newState);
    GameState getState() const;
    
    // 分数和生命管理
    void addScore(int points);
    void loseLife();
    bool isGameOver() const;
    bool isWin() const;
    
    // 游戏对象访问
    void setPaddle(std::shared_ptr<Paddle> paddle);
    void setBall(std::shared_ptr<Ball> ball);
    void setBricks(const std::vector<std::shared_ptr<Brick>>& bricks);
    
    // 事件通知
    void notifyStateChange();
};