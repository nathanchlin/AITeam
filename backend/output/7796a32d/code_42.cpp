// 对象池实现
template<typename T>
class ObjectPool {
private:
    std::vector<T> pool;
    std::vector<bool> used;
    
public:
    T* acquire() {
        for (size_t i = 0; i < used.size(); i++) {
            if (!used[i]) {
                used[i] = true;
                return &pool[i];
            }
        }
        
        // 池中没有可用对象，创建新对象
        pool.emplace_back();
        used.push_back(true);
        return &pool.back();
    }
    
    void release(T* obj) {
        // 找到对象在池中的索引并标记为未使用
        auto it = std::find(pool.begin(), pool.end(), *obj);
        if (it != pool.end()) {
            size_t index = it - pool.begin();
            used[index] = false;
        }
    }
};

// 用于平台和障碍物
ObjectPool<Platform> platformPool;
ObjectPool<Obstacle> obstaclePool;