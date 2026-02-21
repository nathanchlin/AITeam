class QualityManager {
private:
    struct QualitySettings {
        int particleCount;
        bool shadowsEnabled;
        int shadowResolution;
        bool antiAliasing;
        int renderScale;
    };
    
    QualitySettings currentSettings;
    
public:
    void adjustQualityForDevice() {
        // 根据设备性能自动调整质量设置
        DeviceInfo device = getDeviceInfo();
        
        if (device.gpuMemory < 512) {
            currentSettings.particleCount = 100;
            currentSettings.shadowsEnabled = false;
            currentSettings.renderScale = 0.75f;
        } else if (device.gpuMemory < 1024) {
            currentSettings.particleCount = 300;
            currentSettings.shadowsEnabled = true;
            currentSettings.shadowResolution = 512;
            currentSettings.renderScale = 0.9f;
        } else {
            currentSettings.particleCount = 500;
            currentSettings.shadowsEnabled = true;
            currentSettings.shadowResolution = 1024;
            currentSettings.antiAliasing = true;
            currentSettings.renderScale = 1.0f;
        }
    }
};