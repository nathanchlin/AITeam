class ScoreSystem : public System {
private:
    int currentScore;
    int highScore;
    float difficultyMultiplier;
    
public:
    void update(float deltaTime) override;
    void addScore(int points);
    int getCurrentScore() const;
    int getHighScore() const;
    void increaseDifficulty();
    float getDifficultyMultiplier() const;
};

class DifficultyManager {
private:
    float baseSpawnRate;
    float baseEnemySpeed;
    float baseEnemyHealth;
    int scoreThreshold;
    
public:
    void updateDifficulty(int currentScore);
    float getAdjustedSpawnRate() const;
    float getAdjustedEnemySpeed() const;
    float getAdjustedEnemyHealth() const;
};