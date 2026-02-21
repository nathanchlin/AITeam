class EventBus {
private:
    std::vector<std::function<void()>> eventHandlers;
    
public:
    template<typename T> void subscribe(std::function<void(T)> handler);
    template<typename T> void publish(const T& event);
};

// 事件类型示例
struct PlayerHitEvent {
    Entity* player;
    int damage;
};

struct EnemyDestroyedEvent {
    Entity* enemy;
    int points;
};