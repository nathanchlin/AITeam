class EventSystem {
public:
    using EventCallback = std::function<void(const Event&)>;
    
    void subscribe(EventType type, EventCallback callback);
    void publish(const Event& event);
    
private:
    std::unordered_map<EventType, std::vector<EventCallback>> subscribers;
};

// 示例事件类型
enum class EventType {
    BALL_HIT_BRICK,
    BALL_HIT_PADDLE,
    BRICK_DESTROYED,
    GAME_OVER,
    LEVEL_COMPLETE
};