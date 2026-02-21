/**
 * 输入处理模块
 * 管理键盘和鼠标输入
 */
class InputManager {
    constructor() {
        this.keys = {};
        this.mouseX = 0;
        this.mouseY = 0;
        this.setupEventListeners();
    }
    
    /**
     * 设置事件监听器
     */
    setupEventListeners() {
        // 键盘按下事件
        window.addEventListener('keydown', (e) => {
            this.keys[e.key] = true;
        });
        
        // 键盘释放事件
        window.addEventListener('keyup', (e) => {
            this.keys[e.key] = false;
        });
        
        // 鼠标移动事件
        window.addEventListener('mousemove', (e) => {
            this.mouseX = e.clientX;
            this.mouseY = e.clientY;
        });
        
        // 鼠标点击事件
        window.addEventListener('mousedown', (e) => {
            this.keys['Mouse' + e.button] = true;
        });
        
        window.addEventListener('mouseup', (e) => {
            this.keys['Mouse' + e.button] = false;
        });
    }
    
    /**
     * 检查按键是否被按下
     */
    isKeyPressed(key) {
        return !!this.keys[key];
    }
    
    /**
     * 获取鼠标位置
     */
    getMousePosition() {
        return { x: this.mouseX, y: this.mouseY };
    }
    
    /**
     * 重置输入状态
     */
    reset() {
        this.keys = {};
    }
}