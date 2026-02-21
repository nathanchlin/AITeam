class Entity {
private:
    uint32_t id;
    std::vector<std::unique_ptr<Component>> components;
    
public:
    Entity(uint32_t id);
    uint32_t getId() const;
    template<typename T> T* getComponent();
    template<typename T> void addComponent(std::unique_ptr<T> component);
    template<typename T> void removeComponent();
};

class EntityManager {
private:
    std::vector<std::unique_ptr<Entity>> entities;
    std::unordered_map<uint32_t, std::unique_ptr<Entity>> entityMap;
    uint32_t nextId;
    
public:
    Entity* createEntity();
    void destroyEntity(Entity* entity);
    Entity* getEntity(uint32_t id);
    void update(float deltaTime);
    void render();
};