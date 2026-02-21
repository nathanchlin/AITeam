class FrameRateManager {
private:
    float targetFrameTime;
    float accumulatedFrameTime;
    int frameCount;
    float currentFPS;
    
public:
    FrameRateManager() : targetFrameTime(16.67f), accumulatedFrameTime(0), frameCount(0) {}
    
    void update(float deltaTime) {
        accumulatedFrameTime += deltaTime;
        frameCount++;
        
        if (accumulatedFrameTime >= 1.0f) {
            currentFPS = frameCount / accumulatedFrameTime;
            
            // 根据当前FPS调整目标帧时间
            if (currentFPS < 45) {
                targetFrameTime = 20.0f; // 降低到50 FPS
            } else if (currentFPS > 55) {
                targetFrameTime = 16.67f; // 提升到60 FPS
            }
            
            accumulatedFrameTime = 0;
            frameCount = 0;
        }
    }
    
    float getTargetFrameTime() const {
        return targetFrameTime;
    }
};