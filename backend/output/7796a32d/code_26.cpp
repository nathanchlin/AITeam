class PlatformGenerator {
private:
    std::vector<Platform> platforms;
    float lastPlatformY;
    float platformGap;
    
public:
    void generatePlatforms(int level) {
        // 根据关卡调整平台生成参数
        platformGap = 100 + level * 5; // 随关卡增加平台间距
        
        // 生成初始平台
        for (int i = 0; i < 20; ++i) {
            float x = random(0, SCREEN_WIDTH - PLATFORM_WIDTH);
            float y = SCREEN_HEIGHT - i * platformGap;
            platforms.emplace_back(x, y);
        }
        
        lastPlatformY = platforms.back().getY();
    }
    
    void update(float playerY) {
        // 当玩家接近屏幕顶部时生成新平台
        if (playerY < lastPlatformY - SCREEN_HEIGHT * 0.7) {
            float x = random(0, SCREEN_WIDTH - PLATFORM_WIDTH);
            float y = lastPlatformY - platformGap;
            platforms.emplace_back(x, y);
            lastPlatformY = y;
            
            // 移除屏幕外的平台
            platforms.erase(std::remove_if(platforms.begin(), platforms.end(), 
                [](const Platform& p) { return p.getY() > SCREEN_HEIGHT; }), 
                platforms.end());
        }
    }
};