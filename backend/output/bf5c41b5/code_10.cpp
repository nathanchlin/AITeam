class ResourceManager {
public:
    Texture* getTexture(const std::string& path);
    Sound* getSound(const std::string& path);
    Font* getFont(const std::string& path, int size);
    
    void preloadResources();
    
private:
    std::unordered_map<std::string, std::unique_ptr<Texture>> textures;
    std::unordered_map<std::string, std::unique_ptr<Sound>> sounds;
    std::unordered_map<std::string, std::unique_ptr<Font>> fonts;
};