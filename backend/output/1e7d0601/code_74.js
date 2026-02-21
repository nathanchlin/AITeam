// 资源管理器
class ResourceManager {
  constructor() {
    this.resources = new Map();
    this.loadingQueue = [];
    this.loaded = false;
  }
  
  loadResources(resources) {
    return new Promise((resolve) => {
      this.loadingQueue = resources;
      this.loadNextResource(resolve);
    });
  }
  
  loadNextResource(resolve) {
    if (this.loadingQueue.length === 0) {
      this.loaded = true;
      resolve();
      return;
    }
    
    const resource = this.loadingQueue.shift();
    const img = new Image();
    
    img.onload = () => {
      this.resources.set(resource.name, img);
      this.loadNextResource(resolve);
    };
    
    img.src = resource.path;
  }
  
  getResource(name) {
    return this.resources.get(name);
  }
  
  unloadUnusedResources() {
    // 卸载长时间未使用的资源
    const now = Date.now();
    for (let [name, resource] of this.resources) {
      if (resource.lastUsed && now - resource.lastUsed > 60000) {
        this.resources.delete(name);
      }
    }
  }
}

// 使用示例
const resourceManager = new ResourceManager();

// 预加载游戏资源
const resources = [
  { name: 'player', path: 'assets/player.png' },
  { name: 'enemy1', path: 'assets/enemy1.png' },
  { name: 'bullet', path: 'assets/bullet.png' }
];

resourceManager.loadResources(resources).then(() => {
  console.log('所有资源加载完成');
});