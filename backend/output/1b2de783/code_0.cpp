class GameEngine {
private:
    std::vector<std::unique_ptr<System>> systems;
    std::unique_ptr<EntityManager> entityManager;
    std::unique_ptr<ResourceManager> resourceManager;
    bool running;
    
public:
    GameEngine();
    void initialize();
    void run();
    void stop();
    void addSystem(std::unique_ptr<System> system);
    void update(float deltaTime);
    void render();
};