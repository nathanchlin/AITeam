// 资源管理器
class ResourceManager {
    constructor() {
        this.textures = new Map();
        this.audio = new Map();
        this.loadingPromises = new Map();
    }
    
    // 加载纹理
    loadTexture(url) {
        if (this.textures.has(url)) {
            return Promise.resolve(this.textures.get(url));
        }
        
        if (this.loadingPromises.has(url)) {
            return this.loadingPromises.get(url);
        }
        
        const promise = new Promise((resolve, reject) => {
            const img = new Image();
            img.src = url;
            img.onload = () => {
                this.textures.set(url, img);
                this.loadingPromises.delete(url);
                resolve(img);
            };
            img.onerror = () => {
                this.loadingPromises.delete(url);
                reject(new Error(`Failed to load texture: ${url}`));
            };
        });
        
        this.loadingPromises.set(url, promise);
        return promise;
    }
    
    // 加载音频
    loadAudio(url) {
        if (this.audio.has(url)) {
            return Promise.resolve(this.audio.get(url));
        }
        
        if (this.loadingPromises.has(url)) {
            return this.loadingPromises.get(url);
        }
        
        const promise = new Promise((resolve, reject) => {
            const audio = new Audio(url);
            audio.oncanplaythrough = () => {
                this.audio.set(url, audio);
                this.loadingPromises.delete(url);
                resolve(audio);
            };
            audio.onerror = () => {
                this.loadingPromises.delete(url);
                reject(new Error(`Failed to load audio: ${url}`));
            };
        });
        
        this.loadingPromises.set(url, promise);
        return promise;
    }
    
    // 预加载资源
    preloadResources(resources) {
        const loadPromises = resources.map(resource => {
            if (resource.type === 'texture') {
                return this.loadTexture(resource.url);
            } else if (resource.type === 'audio') {
                return this.loadAudio(resource.url);
            }
        });
        
        return Promise.all(loadPromises);
    }
}