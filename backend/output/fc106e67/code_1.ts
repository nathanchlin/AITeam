class GameStateManager {
    private currentState: GameState;
    private previousState: GameState;
    private stateChangeCallbacks: Map<GameState, Function[]> = new Map();
    
    constructor(initialState: GameState = GameState.MENU) {
        this.currentState = initialState;
        this.previousState = initialState;
    }
    
    // 获取当前状态
    public getCurrentState(): GameState {
        return this.currentState;
    }
    
    // 获取上一个状态
    public getPreviousState(): GameState {
        return this.previousState;
    }
    
    // 检查是否处于特定状态
    public isState(state: GameState): boolean {
        return this.currentState === state;
    }
    
    // 改变状态
    public changeState(newState: GameState): void {
        if (this.currentState === newState) return;
        
        this.previousState = this.currentState;
        this.currentState = newState;
        
        // 触发状态变化回调
        this.executeStateCallbacks(newState);
    }
    
    // 注册状态变化回调
    public onStateChange(state: GameState, callback: Function): void {
        if (!this.stateChangeCallbacks.has(state)) {
            this.stateChangeCallbacks.set(state, []);
        }
        this.stateChangeCallbacks.get(state)?.push(callback);
    }
    
    // 执行状态变化回调
    private executeStateCallbacks(state: GameState): void {
        const callbacks = this.stateChangeCallbacks.get(state);
        if (callbacks) {
            callbacks.forEach(callback => callback());
        }
    }
}