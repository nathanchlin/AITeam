class InputManager {
    constructor() {
      this.keys = {};
      this.setupEventListeners();
    }
    
    setupEventListeners() {
      // 监听键盘事件
      window.addEventListener('keydown', (e) => {
        this.keys[e.key] = true;
      });
      
      window.addEventListener('keyup', (e) => {
        this.keys[e.key] = false;
      });
    }
    
    isKeyPressed(key) {
      return this.keys[key];
    }
  }