class ResourceManager {
private:
    std::unordered_map<std::string, std::unique_ptr<Texture>> textures;
    std::unordered_map<std::string, std::unique_ptr<Sound>> sounds;
    std::unordered_map<std::string, std::unique_ptr<Font>> fonts;
    
public:
    Texture* loadTexture(const std::string& path);
    Sound* loadSound(const std::string& path);
    Font* loadFont(const std::string& path, int size);
    void unloadResource(const std::string& path);
    void clearAll();
};